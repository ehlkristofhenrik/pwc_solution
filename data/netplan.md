**Fictive Inc. Enterprise Network Architecture**

This network topology separates public traffic, internal services, corporate users, and sensitive data layers behind dedicated firewalls, VLANs, and security zones.

```mermaid
graph TD
    %% External Internet & Gateway Zone
    subgraph External ["External & Perimeter Zone"]
        Users[Remote Workers & Public Clients]
        WAF["Web Application Firewall (Cloudflare / AWS WAF)"]
        VPN["SSL VPN Gateway / Zero Trust Gateway"]
    end

    %% Edge / Perimeter Security
    subgraph Perimeter ["Perimeter Security Layer"]
        FW_Edge["Primary Edge Firewall (Palo Alto / Fortinet)"]
    end

    %% DMZ Zone
    subgraph DMZ ["Demilitarized Zone (DMZ - VLAN 10)"]
        Edge_Proxy["Nginx / Envoy API Gateways"]
        Pub_LB["External Load Balancers"]
    end

    %% Core Networking & Routing
    subgraph Core ["Core Switch & Network Fabric"]
        Core_Switch["Redundant Core Switches (VLAN Routing)"]
    end

    %% Internal Corporate HQ Zone
    subgraph Corporate ["Corporate HQ Network"]
        subgraph Office_VLAN ["Office Users (VLAN 20)"]
            Workstations[Employee Laptops & Desktops]
        end
        subgraph IoT_VLAN ["Office Infrastructure (VLAN 30)"]
            Printers[Printers & Smart Office Devices]
        end
        subgraph Management_VLAN ["Out-of-Band Mgmt (VLAN 99)"]
            IDP["Identity Provider (Okta / Active Directory)"]
            SIEM["SIEM & Monitoring (Splunk / Datadog)"]
        end
    end

    %% Secure Production Data Center / VPC Zone
    subgraph Production ["Production Environment (Private VPC)"]
        subgraph App_Zone ["Application Tier (VLAN 40 - Private)"]
            App_LB["Internal Load Balancer"]
            App_Servers["K8s Cluster / Microservices Core"]
        end

        subgraph Storage_Zone ["Data Tier (VLAN 50 - Isolated)"]
            DB_Master["Primary Database (PostgreSQL / AWS RDS)"]
            DB_Replica["Read Replicas & Cache (Redis)"]
            Vault["Secrets Vault (HashiCorp Vault)"]
        end

        FW_Internal["Internal Segmented Firewall / Micro-segmentation"]
    end

    %% Network Connections & Traffic Flow
    Users -->|HTTPS / Port 443| WAF
    Users -->|Tunnel / Encrypted| VPN

    WAF --> FW_Edge
    VPN --> FW_Edge

    FW_Edge --> DMZ
    DMZ --> Core_Switch

    Workstations --> Core_Switch
    Printers --> Core_Switch
    IDP --> Core_Switch

    Core_Switch --> FW_Internal
    FW_Internal --> App_Zone

    Edge_Proxy --> App_LB
    App_LB --> App_Servers

    App_Servers --> DB_Master
    App_Servers --> DB_Replica
    App_Servers --> Vault

```

---

**Network Segmentation & Security Controls**

* **Perimeter Security:** All incoming traffic from the internet is scrubbed through the Web Application Firewall (WAF) to filter DDoS attacks and malicious web traffic before reaching the Edge Firewall.
* **Remote Access:** Remote staff access internal resources strictly through a Zero Trust Network Access (ZTNA) agent or SSL-VPN with mandatory Multi-Factor Authentication (MFA).
* **VLAN Segmentation:**
* **VLAN 10 (DMZ):** Houses public-facing API gateways and web servers.
* **VLAN 20 (Corporate):** Employee workstations separated from internal production servers.
* **VLAN 30 (IoT):** Smart office hardware isolated to prevent lateral network movement.
* **VLAN 40 (Production Apps):** Containerized app services closed off from direct internet access.
* **VLAN 50 (Isolated Data):** Strictly controls access to database clusters and secret vaults; reachable only by authorized application pods over encrypted internal links.
* **VLAN 99 (Management):** Out-of-band network for domain control, monitoring, and security logging tools.
