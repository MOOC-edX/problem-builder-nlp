# problem-builder-nlp
xblock-problem-builder-nlp
--------------

This python package is meant to be used as an Xblock Component for OpenEDX LMS and Studio. It's purpose is to provide a Problem Builder with NLP

- Randomized content – WHY?
  + Prevent copy -> Encourage real study
  + Improve quality of education
  + Build resource competency
- Benefits for teacher: Save lots of effort by
  + Create course’s assignment / exam questions easily and quickly
  + Auto-grading assignment
  + Easy assignment reuse (use Content Library)
- Benefits for student: Improve quality of study by
  + Allow try and error (optionally, recommended for learning mode)
  + Problem reset (optionally, recommended for learning mode)
  + Show hints (To Be Implemented)
  + Show answer

# Installation instruction

It depends wether you need to install it in a [DevStack](https://openedx.atlassian.net/wiki/display/OpenOPS/Running+Devstack#RunningDevstack-InstallingtheOpenedXDeveloperStack) or [FullStack](https://openedx.atlassian.net/wiki/display/OpenOPS/Running+Fullstack) OpenEDX instance

## Install on FullStack (production-like environnement)

Several ways of installing a new Xblock on FullStack are documented. We recommend [this one](https://github.com/edx/edx-platform/wiki/Installing-a-new-XBlock) but with the following changes:
 
### Allow All Advanced Components (first time only)
 
- Manually edit the custom settings in /edx/app/edxapp/cms.env.json. 
- Look for attribute "FEATURES", instead of "EDXAPP_FEATURES", and add an item to it:
```
"FEATURES":[
    "ALLOW_ALL_ADVANCED_COMPONENTS": true,
    ...
]
```
- then restart the server but with following command:
```
$ sudo /edx/bin/supervisorctl restart edxapp:
```

### Install problem-builder-nlp

Same as [in the documentation](https://github.com/edx/edx-platform/wiki/Installing-a-new-XBlock#install-an-xblock)

    # Move to the folder:
    cd /edx/app/edxapp
    # Download the XBlock
    sudo -u edxapp git clone https://github.com/MOOC-edX/problem-builder-nlp.git
    # Install it
    sudo -u edxapp /edx/bin/pip.edxapp install problem-builder-nlp/
    # Optionnaly : Remove the installation files
    sudo rm -r problem-builder-nlp

### Reboot if something isn't right ###
In some cases, restart edxapp is necessary to use the XBlock.

    sudo /edx/bin/supervisorctl restart edxapp:

### Activate the CNVideoXBlock in your course ###
Go to `Settings -> Advanced Settings` and set `advanced_modules` to `["problem-template-builder"]`.

### Use it in a unit ###
Select `Advanced -> GCS Problem Builder` in your unit.

### Update
