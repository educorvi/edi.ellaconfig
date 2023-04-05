# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.ellaconfig -t test_service.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.ellaconfig.testing.EDI_ELLACONFIG_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/ellaconfig/tests/robot/test_service.robot
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

Scenario: As a site administrator I can add a Service
  Given a logged-in site administrator
    and an add EllaKonfig form
   When I type 'My Service' into the title field
    and I submit the form
   Then a Service with the title 'My Service' has been created

Scenario: As a site administrator I can view a Service
  Given a logged-in site administrator
    and a Service 'My Service'
   When I go to the Service view
   Then I can see the Service title 'My Service'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add EllaKonfig form
  Go To  ${PLONE_URL}/++add++EllaKonfig

a Service 'My Service'
  Create content  type=EllaKonfig  id=my-service  title=My Service

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Service view
  Go To  ${PLONE_URL}/my-service
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Service with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Service title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
