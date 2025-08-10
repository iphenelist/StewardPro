# Remittance Scheduler Documentation

## Overview

The Remittance Scheduler is an automated system that creates remittance documents based on Tithes and Offerings data collected during specified periods. This system follows SDA (Seventh-day Adventist) church financial standards for remittances to higher church organizations.

## Features

### 1. Automated Remittance Creation
- **Monthly Remittances**: Automatically created on the 1st of each month for the previous month
- **Weekly Remittances**: Automatically created weekly for the previous week (if configured)
- **Configurable Settings**: Enable/disable automation through Church Settings

### 2. Remittance Components
The scheduler automatically calculates and includes:
- **Tithe Amount**: 100% of all tithes collected (remitted to field)
- **Offering to Field**: 58% of regular offerings (as per SDA standards)
- **Special Offerings**: 100% of camp meeting and church building offerings
- **Detailed Breakdown**: Individual remittance items with periods and percentages

### 3. Configuration Options
Through the **Church Settings** doctype:
- Enable/disable automatic remittance creation
- Set remittance frequency (Monthly/Weekly)
- Configure default organization details
- Set up email notifications
- Auto-submit remittances option

## Setup Instructions

### 1. Configure Church Settings
1. Go to **Church Management > Administration > Church Settings**
2. Fill in the required information:
   - Church Information (name, address, contact)
   - Default Organization Details (Conference, Union, etc.)
   - Remittance Automation Settings
   - Notification preferences

### 2. Enable Scheduler
The scheduler is automatically enabled when the app is installed. The following events are configured:
- `monthly`: Creates monthly remittances
- `weekly`: Creates weekly remittances (if enabled)

### 3. Manual Remittance Creation
Use the **Remittance Manager** page for manual operations:
1. Go to **Church Management > Administration > Remittance Manager**
2. Select period dates
3. Preview remittance data
4. Create remittance manually if needed

## Scheduler Logic

### Monthly Scheduler (`create_monthly_remittance`)
- Runs on the 1st of each month
- Creates remittance for the previous month
- Checks if automatic remittance is enabled
- Prevents duplicate remittances for the same period

### Weekly Scheduler (`create_weekly_remittance`)
- Runs weekly (typically on Mondays)
- Creates remittance for the previous week
- Only runs if weekly frequency is configured
- Follows the same duplicate prevention logic

### Data Collection Process
1. **Query Tithes and Offerings**: Retrieves all submitted records for the period
2. **Calculate Totals**: Aggregates tithe, offering, and special offering amounts
3. **Apply SDA Standards**: Calculates 58% of offerings for field remittance
4. **Create Remittance Items**: Detailed breakdown with periods and percentages
5. **Generate Document**: Creates remittance with proper naming and workflow

## API Methods

### Programmatic Access
```python
# Create manual remittance
from stewardpro.church_management.tasks import create_manual_remittance

remittance_name = create_manual_remittance(
    period_start="2024-01-01",
    period_end="2024-01-31",
    remittance_period="Monthly"
)

# Get remittance preview
from stewardpro.church_management.tasks import get_remittance_preview

preview = get_remittance_preview("2024-01-01", "2024-01-31")
```

### REST API Endpoints
```javascript
// Create manual remittance
frappe.call({
    method: 'stewardpro.church_management.tasks.create_manual_remittance',
    args: {
        period_start: '2024-01-01',
        period_end: '2024-01-31',
        remittance_period: 'Monthly'
    }
});

// Get remittance preview
frappe.call({
    method: 'stewardpro.church_management.tasks.get_remittance_preview',
    args: {
        period_start: '2024-01-01',
        period_end: '2024-01-31'
    }
});
```

## Remittance Document Structure

### Main Fields
- **Organization Details**: Type, name, contact information
- **Period Information**: Start/end dates, frequency
- **Financial Amounts**: Tithe, offering to field, special offerings
- **Payment Details**: Mode, reference number, bank details
- **Authorization**: Prepared by, approved by, dates

### Child Table (Remittance Items)
Each remittance includes detailed items:
- **Item Type**: Tithe, Offering to Field, Special Offering
- **Description**: Detailed description with period
- **Amount**: Calculated amount for remittance
- **Percentage**: Percentage of total collected (100% for tithe, 58% for offerings)
- **Period**: From/to dates for the specific item

## Notifications

### Email Notifications
When enabled, the system sends:
- **Creation Notifications**: Immediate notification when remittance is created
- **Summary Reports**: Detailed breakdown to configured recipients
- **Error Notifications**: System administrators notified of any issues

### Notification Content
- Remittance number and organization
- Total amount and breakdown
- Direct link to view the remittance
- Period covered and status

## Error Handling

### Duplicate Prevention
- Checks for existing remittances for the same period
- Prevents creation of duplicate documents
- Logs appropriate messages

### Data Validation
- Ensures period dates are valid
- Verifies contributions exist for the period
- Validates organization settings

### Logging
- All operations logged with appropriate levels
- Errors logged with full traceback
- Success operations logged for audit trail

## Testing

### Test Functions
Use the provided test file:
```python
# Run in Frappe console
from stewardpro.church_management.test_remittance_scheduler import test_remittance_creation, create_sample_data

# Create test data
create_sample_data()

# Test functionality
test_remittance_creation()
```

### Manual Testing
1. Create sample Tithes and Offerings records
2. Configure Church Settings
3. Use Remittance Manager to preview and create remittances
4. Verify calculations and remittance items

## Troubleshooting

### Common Issues
1. **No remittances created**: Check if automatic remittance is enabled in Church Settings
2. **Missing data**: Ensure Tithes and Offerings records are submitted (docstatus = 1)
3. **Calculation errors**: Verify SDA percentage calculations (58%/42% split)
4. **Notification failures**: Check email settings and recipient addresses

### Debug Mode
Enable debug logging to trace scheduler execution:
```python
frappe.logger().setLevel("DEBUG")
```

## SDA Compliance

The scheduler follows SDA financial standards:
- **Tithe**: 100% remitted to Conference/Union
- **Regular Offerings**: 58% to field, 42% retained by local church
- **Special Offerings**: 100% remitted as designated
- **Proper Documentation**: Detailed breakdown for audit purposes

This automated system ensures consistent, accurate, and timely remittances while maintaining full compliance with SDA financial protocols.
