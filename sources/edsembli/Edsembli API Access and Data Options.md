Edsembli offers several API access capabilities and integration methods designed to connect its Human Resources & Payroll (HRP), Finance (FIN), and Student Information Systems (SIS) with third-party applications.11

### **API Access Capabilities**

Edsembli utilizes a **"standard API connection"** for its core modules.21 Specific API standards and protocols include:3

* **OneRoster API:** Edsembli SIS supports the OneRoster standard (typically version 1.1), which is a widely recognized technical specification for the secure exchange of student data, rosters, and grades.4
* **OData/REST APIs (Finance/HRP):** Because Edsembli’s financial and HRP systems (formerly Sparkrock) are powered by **Microsoft Dynamics 365 Business Central**, they leverage modern REST/OData APIs. This allows for standard CRUD (Create, Read, Update, Delete) operations on business objects like employees, vendors, and invoices.3

* **Web Services:** The software includes web services for specific data exchanges, such as the "Xello Data Exchange" module used for student career planning.5

### **API Applications and Use Cases**

The APIs are typically applied in the following ways:

* **Rostering:** Automatically provisioning student and teacher accounts in third-party learning platforms (e.g., Google Classroom, Brightspace) before the school year begins.
* **Grade Synchronization:** Pulling marks and comments from classroom tools (like Edsby) directly into the Edsembli Markbook to generate report cards.
* **Data Retrieval:** Exporting attendance data, student demographics, or financial ledger codes for analysis in external business intelligence (BI) tools.
* **Authentication:** Integrating with Google Cloud Platform using OAuth 2.0 to allow staff and students to sign in with their existing school credentials.5

### **Finding the API Key and Credentials**

API keys are generally managed at the administrative or "Tenant" level rather than by individual teachers:

* **OneRoster Key:** Edsembli provides a unique **apikey** for each specific tenant (school board).6 To enable this, administrators must set up a generic staff record named oneroster and link a unique vendor username to it.7
* **OAuth Credentials:** For Google or Microsoft integrations, administrators generate a **Client ID** and **Client Secret** within the respective cloud console (e.g., Google Cloud Platform) and then enter these values into the Edsembli WebAdmin under **Setup \> Email Settings** or **Security**.8
* **OneRoster URL:** The base URL for OneRoster documentation and testing is typically https://oneroster.edsemblicloud.com/swagger/index.html.

### **Import and Export Options**

Edsembli provides several manual and automated options for moving data:

| Action | Supported Formats | Description |
| :---- | :---- | :---- |
| **Exporting Reports** | CSV, PDF, XML | Available through the "Quick Reports" tile and "Data Mining" views in the Student Reports section. |
| **Importing Marks** | MWM, CSV | Marks from third-party tools like Edsby use the "Maplewood Format" (.MWM), a comma-delimited file with specific quoting rules. |
| **OnSIS Submissions** | XML, CSV | Used for mandatory provincial reporting; batch files are typically generated in XML for ministry uploads. |
| **General Imports** | CSV, TSV, XML, JSON | Through partner integrations like Clevr, the system can clean and reshape complex JSON or XML files to update student records.6  |

For complex or custom data export requirements that fall outside the standard API, Edsembli also offers a paid professional service to build custom integrations.91
