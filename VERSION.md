# Version History

This is the version history for PageFund development.

## Version 0.27.0

Release date: TBD

### Additions

* Accessbility for disabled users
* Add users to SendGrid contact list when they sign up

### Changes

* Minify JS and CSS

### Fixes

* Navigation buttons were off-center


## Version 0.26.0

Release date: 02/02/2018

69 files changed, 1007 insertions(+), 242 deletions(-)

### Additions

* Social signup design
* Error page for when Page or Campaign doesn't exist
* Custom 404 and 500 pages
* Success, warning, and error messages on form feedback
* Logging all Stripe webhooks
* Styling for "Forgot password request" and "Forgot password reset" pages
* Form error messages on auth pages
* Facebook and Twitter share buttons
* Open Graph metadata

### Changes

* Hooked PageFund notification preferences into SendGrid email functions
* Removed login/logout messages

### Fixes

* HTML5 compliance
* Twitter signup/login wasn't working
* Logo wasn't showing up correctly in Gmail
* Changed "Forgot password reset" inputs to password instead of plaintext


## Version 0.25.0

Release date: 02/01/2018

33 files changed, 495 insertions(+), 179 deletions(-)

### Additions

* Features page
* All form inputs have a label for ARIA and SEO
* Sitemap

### Changes

* Form validation site-wide
* Vote participant edit design
* Home page image width
* Home page mobile breakpoints
* "Get started" design

### Fixes

* None


## Version 0.24.0

Release date: 01/30/2018

50 files changed, 1093 insertions(+), 526 deletions(-)

### Additions

* FAQ design
* Email design
* Change password feature
* Page verified check

### Changes

* None

### Fixes

* Emails weren't working correctly and SendGrid templates weren't formatted correctly
* Page and Campaign admin/manager permissions weren't working as expected


## Version 0.23.0

Release date: 01/29/2018

68 files changed, 1234 insertions(+), 832 deletions(-)

### Additions

* Login design
* Signup design
* Alt tags and titles on images
* Meta descriptions for static pages
* Donate design
* "How it works" section on "Get Started" page
* robots.txt

### Changes

* Home design
* Put all javascript at the end of files for faster page loads

### Fixes

* None


## Version 0.22.0

Release date: 01/28/2018

43 files changed, 499 insertions(+), 529 deletions(-)

### Additions

* Placeholder text for when comments, donations, and Campaigns don't exist
* Alerts for required fields in forms
* All new categories to Pages
* Text placeholders for areas on the site that have nothing, like no donations/comments
* Social media links in footer

### Changes

* Removed all debugs
* Removed NULL fields from database where unneccessary

### Fixes

* New user signup emails weren't going out


## Version 0.21.0

Release date: 01/27/2018

61 files changed, 574 insertions(+), 772 deletions(-)

### Additions

* Active and past Campaigns on Page dashboard

### Changes

* Mobile design for Page/Campaign dashboards
* Removed location site-wide
* Auto-generating Page/Campaign slug on creation and letting users change it in the dashboard
* Removed majority of helper text on forms and stated which fields are optional
* Resized form fields for better readability

### Fixes

* Page wasn't getting populated on Campaign creation when coming from a Page instead of a new search
* Page monthly donations weren't working
* Deleting Page monthly donations weren't working
* Can't invite managers with a blank permission set


## Version 0.20.0

Release date: 01/26/2018

29 files changed, 1091 insertions(+), 318 deletions(-)

### Additions

* Campaign dashboard design

### Changes

* Renamed dashboard and admin links, re-organized social links

### Fixes

* Large images weren't uploading properly


## Version 0.19.0

Release date: 01/25/2018

24 files changed, 1446 insertions(+), 339 deletions(-)

### Additions

* Page dashboard design

### Changes

* None

### Fixes

* None


## Version 0.18.0

Release date: 01/23/2018

40 files changed, 1145 insertions(+), 121 deletions(-)

### Additions

* Reporting for Page and Campaign images
* Get started page
* Create Page design
* Create Campaign design

### Changes

* None

### Fixes

* Active campaigns weren't showing up on Campaigns if the Campaign goal was $0
* Campaign end date and goal are required


## Version 0.17.1

Release date: 01/21/2018

15 files changed, 138 insertions(+), 71 deletions(-)

### Additions

* None

### Changes

* Identifying the logged-in user in their profile
* Admin site URL

### Fixes

* Issue where Campaign admins couldn't view the Campaign dashboard
* Subscribe button issues
* Error page for bad image size/type wasn't loading
* Expired invitations
* Add card to profile
* Images getting cropped in circles


## Version 0.17.0

Release date: 01/19/2018

26 files changed, 788 insertions(+), 303 deletions(-)

### Additions

* Profile design

### Changes

* None

### Fixes

* None


## Version 0.16.1

Release date: 01/18/2018

14 files changed, 217 insertions(+), 22 deletions(-)

### Additions

* None

### Changes

* None

### Fixes

* Images are no longer warped when placed in a circle on the site


## Version 0.16.0

Release date: 01/17/2018

32 files changed, 273 insertions(+), 172 deletions(-)

### Additions

* Search design
* Error logging on production server

### Changes

* None

### Fixes

* "Notes" reporting feature works again
* Search results with Pages/Campaigns that have $0 donated


## Version 0.15.0

Release date: 01/16/2018

36 files changed, 649 insertions(+), 175 deletions(-)

### Additions

* Image gallery for Pages
* Campaign design

### Changes

* Force user into mm/dd/yyyy inputs for birthday
* Prevent user from setting Campaign end date as date prior to today

### Fixes

* Can't donate to a Campaign if it has ended


## Version 0.14.0

Release date: 01/15/2018

25 files changed, 207 insertions(+), 102 deletions(-)

### Additions

* Print donation history for taxes

### Changes

* Removed Instagram share and replaced with full-row Page website
* Replaced manual emails with SendGrid templates
* Added a "create" link to nav and moved the "About" and "FAQ" links to the footer

### Fixes

* Hide user profile picture in Page donation history if user chose "anonymous donation"
* Breakpoints on Page allow for less clutter for Page information
* Can only add/edit vote participants if the Campaign is type "vote"


## Version 0.13.0

Release date: 01/10/2018

8 files changed, 92 insertions(+), 18 deletions(-)

### Additions

* Vote participant images

### Changes

* None

### Fixes

* None


## Version 0.12.1

Release date: 01/09/2018

31 files changed, 335 insertions(+), 43 deletions(-)

### Additions

* None

### Changes

* None

### Fixes

* Removed django-contrib-comments due to bug and created custom Comments app


## Version 0.12.0

Release date: 01/08/2018

149 files changed, 635 insertions(+), 3284 deletions(-)

### Additions

* Dynamically add/remove vote participants for Campaign

### Changes

* Removed voting system on comments and FAQs
* Removed comment system and implemented django-contrib-comments

### Fixes

* Vote participant forms allow you to add more than two choices
* Campaign creation form prevents semicolons and other unwanted characters in the Campaign slug
* Force user to pick a Page when creating a Campaign, prevent otherwise


## Version 0.11.1

Release date: 01/04/2018

120 files changed, 3008 insertions(+), 586 deletions(-)

### Additions

* Notes system for communication between PageFund and users
* Home page design
* Tooltips
* Page design

### Changes

* None

### Fixes

* Donation amount rendered wrong in templates for past Campaigns


## Version 0.11.0

Release date: 12/20/2017

86 files changed, 2532 insertions(+), 561 deletions(-)

### Additions

* Campaign end dates
* Campaign voting
* Added "other" option to Page categories
* Preset donation amounts ($5, $10, $25, $50, $100)
* Managers can remove themselves from Pages/Campaigns as managers
* Content for Terms of Service and Privacy Policy
* Users can add change the Page bank account
* Integration with Stripe errors

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
