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
$ sudo /edx/bin/supervisorctl restart edxapp_worker:
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
    sudo /edx/bin/supervisorctl restart edxapp_worker:

### Activate the ProblemBuilderNLP in your course ###
Go to `Settings -> Advanced Settings` and set `advanced_modules` to `["problem-template-builder"]`.

### Use it in a unit ###
Select `Advanced -> GCS Problem Builder` in your unit.

### Tips & Tricks to enable adding customed xBlock into Library Content 
#### (This tips and tricks WORKED on FICUS but NEWER VERSION! Need check why???)
1. In this file: /edx/app/edxapp/edx-platform/cms/djangoapps/contentstore/views/item.py#L618-L623
comment out following lines:

NOTE: (This tips and tricks WORKED on FICUS but NEWER VERSION! Need check why???)
```
#if isinstance(usage_key, LibraryUsageLocator):
    #    # Only these categories are supported at this time.
    #   if category not in ['html', 'problem', 'video']:
    #       return HttpResponseBadRequest(
    #          "Category '%s' not supported for Libraries" % category, content_type='text/plain'
    #      )
```

2. in this file: /edx/app/edxapp/edx-platform/cms/envs/common.py, Add our xblock to component list:

NOTE: (This tips and tricks WORKED on FICUS but NEWER VERSION! Need check why???)
```
# Specify XBlocks that should be treated as advanced problems. Each entry is a
# dict:
#       'component': the entry-point name of the XBlock.
#       'boilerplate_name': an optional YAML template to be used.  Specify as
#               None to omit.
#
ADVANCED_PROBLEM_TYPES = [
    {
    ...
    },
    {    
        'component': 'tb-math-problem-template-builder',
        'boilerplate_name': None,
    },
]
```

3. For ficus.master, it required additional modification in file /edx/app/edxapp/edx-platform/cms/djangoapps/contentstore/views/component.py, as following to add xblock into Content Library: 

NOTE: (This tips and tricks WORKED on FICUS but NEWER VERSION! Need check why???)
```
# TODO: canhdq changed this
        # if category == 'problem' and not library: # Comment out this line to add advanced component into content library
        if category == 'problem': # Replaced above line by this line (it worked for ficus.master BUT newer version???)
```


### Uninstall xblock ###
- switch to user edxapp
```
sudo -u edxapp -Hs
```

- Activate edxapp venvs
```
source /edx/app/edxapp/venvs/edxapp/bin/activate
```

- List installed xblock with partial text of its name 'xblock'. Locate the xblock name to uninstall.
```
pip list | grep xblock
```

- Uninstall an installed xblock by its name 'xblock-problem-template-builder' with command:
```
pip uninstall xblock-problem-template-builder
```
