# Version History

This is the version history for PageFund development.


## Version 0.11.0

Release date: TBD

### Additions

* Campaign end dates
* Campaign voting
* Added "other" option to Page categories
* Preset donation amounts ($5, $10, $25, $50, $100)
* Managers can remove themselves from Pages/Campaigns as managers
* Content for Terms of Service and Privacy Policy
* Users can add change the Page bank account

### Changes

* Campaigns can be created from the home page or from a specific Page
* Campaign admins and managers get automatically subscribed to the Campaign when it is created or they accept a manager invitation
* Users that are signing up only need their email instead of name, birthday, state, etc.
* Removed "nonprofit number" from Pages
* Removed "subscribe" option from Pages/Campaigns if user is an admin or manager
* Page creation process happens in multiple steps

### Fixes

* Filtered expired Campaigns off the home page
* Linebreaks added to Page/Campaign descriptions
* Don't have to enter SSN or Terms of Service agreement when editing a Page
* Donations can't be negative anymore, and have a maximum of $999,999 to accommodate Stripe's maximum
* Redirect issue when subscribing to a Page/Campaign while logged out
* Forms weren't taking into consideration what users chose for their Page/Campaign slugs and was instead being automatically created on the back-end


## Version 0.10.0

Release date: 11/17/2017

90 files changed, 3146 insertions(+), 776 deletions(-)

### Additions

* Users can set their email notification preferences
* Page and Campaign dashboard
* Users can donate if they don't have an account
* Tiebreakers for trending pages and campaigns
* Error handling and email notifications when there is an Stripe connection error
* FAQs
* About Us placeholder page
* Terms of Service placeholder page
* Users can subscribe to Campaigns
* Voting on comments and FAQs

### Changes

* Any personal preferences about pages and campaigns, such as subscriptions, were moved from the home page to the user's profile page
* Removed the option for users to cover Stripe fees

### Fixes

* Searches threw an error when filtering by category 
* Setting manager permissions on Pages generated an error


## Version 0.9.0

Release date: 10/30/2017

96 files changed, 4851 insertions(+), 1267 deletions(-)

### Additions

* Managed campaigns added to user profile
* Option to cover Stripe fees when donating
* Option to hide donation amount
* Hooked into Stripe donations to populate total donation amount and count on Pages and Campaigns
* Donate with default saved card
* Recurring donations
* Upload multiple images at a time to a Page, Campaign, or user profile

### Changes

* Moved to fat models
* Deleted the old mail server (RIP) and moved to G Suite and Sendgrid
* Changed donation amounts from Integer to Decimal
* Moved helper functions from views to utils

### Fixes

* Campaign invitations showed up blank on the user profile
* Users couldn't update their name properly
* Image uploads failed if they were the first image to be uploaded to their respective Page, Campaign, or user profile


## Version 0.8.0

Release date: 10/06/2017

50 files changed, 1696 insertions(+), 92 deletions(-)

### Additions

* Donate to Campaigns
* Trending Pages added to Home
* Trending Campaigns added to Home
* With the right permissions, users can edit and delete existing pictures in Pages, Campaigns, and their profile
* Users can save credit cards during a donation
* Users can update their credit card information on their profile

### Changes

None

### Fixes

None


## Version 0.7.0

Release date: 09/29/2017

### Additions

* Donate to Pages
* New fields for Page: type (nonprofit, religious, other), website URL, contact email and phone, bank account and routing number, SSN, full address, 501c number
* Cron job to set manager invitations, general invitations, and 
* User's donations on User Profile
* Top donors on Page

### Changes

* Moved first/last name from UserProfile model to User model
* Removed field for Page: type (organization)

### Fixes

* Managers weren't getting prompted to confirm before deleting a Page
* Managers are now subscribed to Pages when they accept their Manager invitation
* Creating a custom account on Stripe failed


## Version 0.6.0

### Additions

* Production server
* Google authentication
* Facebook authentication
* New field for User: birthday
* 'Forgot password' system

### Changes

None

### Fixes

None


## Version 0.5.0

### Additions

* Error system for explicit error handling
* Page and Campaign images
* Show user's name in the navigation menu
* 'List all' option on Search page for Pages and Campaigns
* New field for Page: date created
* New field for Campaign: date created
* 'Upload image' added to manager permissions options
* Invite people to join PageFund
* Search box on Home

### Changes

* Everything is archived now instead of deleted forever
* Moved site URL to config.py for easier development between the team
* User must confirm they want to delete a Page/Campaign

### Fixes

* Campaign admins saw double permissions (admin + manager)


## Version 0.4.0

### Additions

* Comment/Reply system on Pages and Campaigns
* Email created for social accounts: social@page.fund
* New fields for Page: city, state, type
* Filter by 'state' on Search page
* Campaigns added to Search results
* List all Pages that a user managers on their User Profile

### Changes

* Search scripts redone to remove 'blinking' effect on keyUp action

### Fixes

* Couldn't invite a user to manage a Page
* Pressing 'Enter' when searching would submit the form and clear the search bar
* Page admins saw double permissions (admin + manager)


## Version 0.3.0

### Additions

* Admin/manager permission system for Pages and Campaigns
* Email notifications go to Page admins when a Campaign is created for their Page
* Pending sent invitations on User Profile
* List all Pages that a user is an admin of on their User Profile

### Changes

* 'Redirects' testing structure in all tests
* Server time changed from UTC to CST
* Changed Campaign URLs to include the campaign.pk so that Campaign slugs are no longer unique

### Fixes

None


## Version 0.2.0

### Additions

* Mail server
* Email notifications

### Changes

* Anyone can create a campaign, not just Page admins
* Secure credentials moved to config.py

### Fixes

None


## Version 0.1.0

### Additions

* Authentication system
* Search
* Pages
* Campaigns
* Page subscriptions
* Home; user feed
* User profile
* Page and Campaign administrative actions for the creator

### Changes

None

### Fixes

None
