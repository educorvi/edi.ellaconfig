# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.ellaconfig -t test_servicebutton.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.ellaconfig.testing.EDI_ELLACONFIG_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/ellaconfig/tests/robot/test_servicebutton.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Servicebutton
  Given a logged-in site administrator
    and an add Service form
   When I type 'My Servicebutton' into the title field
    and I submit the form
   Then a Servicebutton with the title 'My Servicebutton' has been created

Scenario: As a site administrator I can view a Servicebutton
  Given a logged-in site administrator
    and a Servicebutton 'My Servicebutton'
   When I go to the Servicebutton view
   Then I can see the Servicebutton title 'My Servicebutton'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Service form
  Go To  ${PLONE_URL}/++add++Service

a Servicebutton 'My Servicebutton'
  Create content  type=Service  id=my-servicebutton  title=My Servicebutton

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Servicebutton view
  Go To  ${PLONE_URL}/my-servicebutton
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Servicebutton with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Servicebutton title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
