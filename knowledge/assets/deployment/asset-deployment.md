---
id: kb-assets-deployment-asset-deployment
title: Asset Deployment
canonical_path: knowledge/assets/deployment/asset-deployment.md
summary: 'This process needs to be followed for every assignment and deployment of assets to, but not limited to:'
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Asset Deployment
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
created: '2026-02-17'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
steps:
- Review the imported procedure body below and confirm the documented scope matches the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or incomplete.
related_articles:
- kb-assets-deployment-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

This process needs to be followed for every assignment and deployment of assets to, but not limited to:

- New hire employees/contractors
- Replacement of assets for existing employees/contractors
- Devices assigned to employees for events or testing
- Or for any other situation where IT hands off a device to an employee or contractor.

#### When handling an asset and providing to a user it’s important to log this asset properly within the [Asset <ASSET_MANAGEMENT_SYSTEM> tracker](<INTERNAL_URL>) .

# Find an Available Laptop

1. Determine if the user needs a [Mac Acquisition and Configuration Mac](../acquisition/mac-acquisition-and-configuration.md) or [Windows Deployment Windows](windows-deployment.md) device
2. Open the **<COMPANY_NAME> IT** base in <ASSET_MANAGEMENT_SYSTEM>.
3. Navigate to the **Inventory** table.
4. Switch to the **In Stock &** **Ready To Give** view to see laptops that are cleaned, erased, and ready for deployment.
  1. If no devices are available in **In Stock & Ready To Give** . Find an appropriate device in **Needs Setup& Erase** or **Term Hold** . Follow steps to prepare this device.
5. Select the appropriate device and find it physically in storage.

# Prepare the Laptop for Deployment

- If the device has not been erased, **Reimage** the laptop according to the current **Hardware Asset Policy** standards.
- **Physically clean and inspect** the device before deployment:
  - Wipe surfaces
    - Dust thoroughly
    - Check for visible damage
- Check the laptop’s configuration to ensure it meets the employee’s needs:
  - Ensure that the laptop is running the **latest software version** . This is vital to ensure no security updates have been missed before deployment.
    - Ensure that the model is the same or newer than the user's current machine if we are replacing the device.
- Physically prepare the laptop for delivery:
  - For in-person deployment: Prepare the laptop for handoff. Clean the laptop and pair it with the appropriate charger and charging cable
    - For shipping: Package the laptop securely, label it, and arrange delivery with the courier service.

# Add the Assignee

1. Open the record for the selected laptop.
2. In the **Assignee** field, link the record to the employee receiving the laptop:
  1. Use the dropdown menu to select the employee from the **Employees & Offboarding** table.

## Update the Laptop’s Status

After adding the assignee, change the **Status** field from **Ready To Give** to **Reserved** .

# Deploy and Confirm Delivery

1. If shipping, add the expected delivery date to the **Delivery Date** field and record the tracking number in the **Notes** field if available. Change the status to **In Transit** once the device is handed to the courier.
  1. **Only one charger is issued** per laptop. Ensure it is included and noted.
    2. **Include the** [**New Hire Laptop Note**](<INTERNAL_URL>) with every laptop being shipped.
2. Once the device is physically handed to the user or delivery is confirmed, update the **Status** field to **Deployed** to finalize the assignment.
3. **macOS-only** (for now): Ensure that the user has [registered their machine’s **<MFA_APPLICATION>**](<INTERNAL_URL>) application with their <IDENTITY_PROVIDER> account.

# Additional Notes

- Follow this process to ensure all devices are tracked accurately.
- Adding the assignee before changing the status minimizes tracking errors.
- If a device requires additional setup before deployment, set the **Status** to **Needs Setup/Erasing** and complete the setup before marking as **Ready To Give** .

This structured workflow ensures devices are properly assigned, minimizing errors and maintaining inventory accuracy.

<ASSET_MANAGEMENT_SYSTEM> tracking Guide for more insight [here](<INTERNAL_URL>)
