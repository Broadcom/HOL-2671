
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*        HOL-2671 VMware NSX Advanced Load Balancer (Avi Networks) labs         *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *

Explore VMware NSX Advanced Load Balancer by Avi Networks to see how it easy it is to apply load
balancing, web application firewall and container ingress to any application in a multi-cloud
environment.

Product Details:

-  NSX Advanced Load Balancer 30.2.1
-  vSphere 8.0
-  Pseudo-dual-site configuration  (two Avi controllers, single NSX/vCenter.  Split by T1 and edge)

For the vSphere Web Client, use:
User name: administrator@vsphere.local
Password: 

For the Avi Controllers, use:
User Name: admin
Password: 

For NSX Manager, use:
User Name: admin
Password: 

You can enter these passwords by hand, or use the VMware Learning Platform "Send Text" control and copy/paste from Lab Manual.

* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*         HOL-2671-01 VMware NSX Advanced Load Balancer by Avi Networks         *
*                               Getting Started                                 *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *

===============
== Module 1  ==
===============
** Introduction to Cloud Connectors **

Go over the Day 0 operation of configuring cloud connector to allow the Avi Controller to discover
and automate Virtual Service placement in vSphere environment.

===============
== Module 2 ==
===============
** Introduction to Applications (Virtual Services and Related Components) **

Configure Virtual Services, Pools, Health Monitors, Certificates, SSL Profile, Application Profile.

===============
== Module 3 ==
===============
** Introduction to Service Engine Groups  **

Introduction to Service Engine High Availability, sizing and placement configuration.

===============
== Module 4  ==
===============
** Introduction to Application Scaling **

Scale out, Scale in, Migrate Virtual Service, Disable Virtual Service for maintenance.

===============
== Module 5  ==
===============
** Introduction to Application Services and Security

IP address Groups, String Groups, Network Security Policies, HTTP Security Policies, HTTP Request
and Response policies and Traffic Management Scripts - DataScripts (based on Lua).

===============
== Module 6  ==
===============
** Introduction to Application Troubleshooting **

Using Events, Alerts, Logs and analytics dashboard to troubleshoot your application.

===============
== Module 7  ==
===============
Leveraging Automation Migration Toolkit to accelerate migrations from F5 to VMware NSX Advanced
Load Balancer

The goal of this module is to introduce and review the foundation components behind migration
toolkit.



* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*         HOL-2671-02 VMware NSX Advanced Load Balancer by Avi Networks         *
*                         Global Server Load Balancing                          *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *

Get familiar with the Global Server Load Balancing (GSLB) features of VMware NSX Advanced Load
Balancer by Avi Networks. These modules cover cross-site high availability and location awareness
for a better client experience.

===============
== Module 1  ==
===============
** Global Server Load Balancer Infrastructure Dependencies **

The goal of this module is to introduce and review the foundation components behind Global Server
Load Balancing infrastructure.

===============
== Module 2  ==
===============
** Building a Global Server Load Balancing Infrastructure **

The goal of this module is to focus on GSLB infrastructure build out.

===============
== Module 3  ==
===============
** Creating a Basic Global Service **

The goal of this module is to focus on basic GSLB service components and functionality, learn the
basics of GSLB service.

===============
== Module 4  ==
===============
**Creating an Advanced Global Service **

The goal of this module is to focus on advanced capabilities of GSLB services, deep dive on the
various advanced components and requirements behind Advanced GSLB service creation.

===============
== Module 5  ==
===============
** Creating a Geo-Aware Global Service **

The goal of this module is to focus on Geo capabilities of GSLB services, deep dive on the various
Geo components and requirements behind Advanced Geo GSLB service creation.

===============
== Module 6  ==
===============
** DNS Policy and Static DNS Records Management **

The goal of this module is to focus on advanced capabilities of DNS Virtual Services, related DNS
policy functionality as well as other DNS features.


* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*         HOL-2671-03 VMware NSX Advanced Load Balancer by Avi Networks         *
*                           Web Application Security                            *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *


Discover how you can evolve your application security with NSX Advanced Load Balancer's intelligent
WAF features. Learn how to increase performance and reduce false positives of your security policy
by implementing whitelisting, positive security model with application learning, and signature
exclusions.

===============
== Module 1  ==
===============
** Introduction to NSX ALB Virtual Services and web application vulnerabilities **

Show the setup of vulnerable web application, sql injection, cross site scripting, and remote
execution attack vectors.

===============
== Module 2  ==
===============
** DDoS Attacks Mitigation **

Demonstrate a DDoS attack and our mitigation features.

===============
== Module 3  ==
===============
** Enabling and tuning WAF Policy on a Virtual Service **

Create and tune a WAF policy.

===============
== Module 4  ==
===============
** 	WAF Positive Security and Learning Mode **

Configure positive security model with learning and show the benefits of PSM versus a negative
security model.

===============
== Module 5  ==
===============
** Core Rule Set Signatures and Exceptions **

Show how to use allowlists to override core rule set behavior.

===============
== Module 6  ==
===============
** Introduction to Logs and WAF Analytics **

Show log hits from various test traffic, show analytics.

* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*         HOL-2671-04 VMware NSX Advanced Load Balancer by Avi Networks         *
*                           Avi Kubernetes Operator                             *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *


Explore the Avi Kubernetes Operator (AKO) and see how it enables enterprise load balancing and security features for your container ingress.

===============
== Module 1  ==
===============
** Introduction to NSX ALB Infrastructure **

Show the setup of basic virtual services.

===============
== Module 2  ==
===============
** Introduction to AKO (Avi Kubernetes Operator) **

Introduction to AKO and how it works.

===============
== Module 3  ==
===============
** Deploying AKO **

How to deploy and configure AKO.

===============
== Module 4  ==
===============
** 	AKO Advanced Features **

Enhanced Virtual Hosting overview.

===============
== Module 5  ==
===============
** Creating HTTPrule and Hostrule CRDs **

Using CRDs to adjust the default behavior of AKO-created virtual services.

===============
== Module 6  ==
===============
** Introduction to GSLB with AMKO **

How AMKO works with AKO to build global services.

===============
== Module 7  ==
===============
** Using AMKO CRDs to deploy global services **

Use AMKO to deploy global kubernetes services.

===============
== Module 8  ==
===============
** Node Port Local overview **

Learn the differences between ClusterIP, NodePort, and NodePortLocal.


* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*         HOL-2671-05 VMware NSX Advanced Load Balancer by Avi Networks         *
*                                Migration                                      *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *


The goal of this lab is to introduce and review the foundation components behind migration toolkit. You will learn
how to migrate virtual services from F5 and from NSX-T load balancer.

===============
== Module 1  ==
===============
** Overview of NSX ALB architecture, including Virtual Services, Pools, Service Engines, cloud connector **

Learn the basics of Avi architecture.

===============
== Module 2  ==
===============
** Leveraging Automation Migration Toolkit to accelerate migrations from F5 to VMware NSX Advanced Load Balancer **

Explore how to migrate from F5 load balancers to Avi.

===============
== Module 3  ==
===============
** Using the migration toolkit to migrate from NSX-T LB to Avi and optionally build cutover automation **

Migrate and cut over from NSX-T LB to Avi.


* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *
*                      HOL-2671-06 VMware Avi Load Balancer                     *
*                                Automation                                     *
* - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - *


The goal of this lab is to give you the tools necessary to start automating your load balancer deployments

===============
== Module 1  ==
===============
** Overview of Avi API **

Postman, swagger, CLI tools


===============
== Module 2  ==
===============
** Avi with Ansible **


===============
== Module 3  ==
===============
** Avi with Terraform **


===============
== Module 4  ==
===============
** Avi with Aria Automation **
