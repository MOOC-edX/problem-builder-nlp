import logging
import json
from lxml import etree
from collections import namedtuple
from itertools import chain
from lazy.lazy import lazy
from xblock.core import XBlock
from xblock.exceptions import NoSuchViewError, JsonHandlerError
from xblock.fields import Boolean, Scope, String, Integer, Float, List, ScopeIds
from xblock.fragment import Fragment
from xblock.runtime import MemoryIdManager

from xblock.validation import Validation
from xblockutils.helpers import child_isinstance
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin, ThemableXBlockMixin
#from xmodule.modulestore.xml import CourseLocationManager
from uuid import uuid4
from opaque_keys.edx.keys import CourseKey


from xblockutils.studio_editable import (
    NestedXBlockSpec, StudioEditableXBlockMixin, StudioContainerWithNestedXBlocksMixin,
    )

try: 
    from workbench.runtime import WorkbenchRuntime
except ImportError:
    WorkbenchRuntime = False



log =logging.getLogger(__name__)
loader = ResourceLoader(__name__)


def _(text):
    return text
class FancyXBlock( XBlock , StudioEditableXBlockMixin):
    CATEGORY = 'tb-fancy'
    STUDIO_LABEL = _(u"Input Template")
    display_name = String (
        display_name = _("Title"),
        scope = Scope.settings,
        default = _("Stuff")
    )
    question = String (
        display_name = _("question"),
        scope = Scope.content,
        default = _("Stuff")
        )
    editable_fields = ('display_name', 'question')

    def student_view(self, context = None):
        local_context = {}
        if context is None:
            local_context = {
                'question' : self.question
            }
        else:
            local_context = {
                'question' : self.question
            }


        frag = Fragment()
                
        frag.add_content(loader.render_template('templates/question_template.html', local_context))
        
        return frag

class TemplateBlock(StudioContainerWithNestedXBlocksMixin, XBlock, StudioEditableXBlockMixin):
    display_name = String (
        display_name = _("Title"),
        help =_("The title of this Xblock"),
        scope = Scope.settings,
        default = _("Stuff")
        )
    question = String (
        display_name = _("Question"),
        default = None,
        scope = Scope.settings,
        multiline_editor = True
        )
    editable_fields = ('display_name', 'question')
    @property
    def allowed_nested_blocks(self):
        additional_blocks = []
        try:
            from xmodule.video_module.video_module import VideoDescriptor
            additional_blocks.append(NestedXBlockSpec(VideoDescriptor, category='video', label=_(u"My Video")))
        except ImportError:
                pass
        try:
            from imagemodal import ImageModal
            additional_blocks.append(NestedXBlockSpec(ImageModal, category='imagemodal', label=_(u"Image Modal")
                                                                    ))
        except ImportError:
            pass
        return [FancyXBlock] +  additional_blocks
    def author_edit_view(self, context = None):
        #from xmodule.modulestore.xml import CourseLocationManager
        course_key = getattr(self.runtime, 'course_id', 'all')
        block_type = u'tb-fancy'
        block_id = u'{}'.format(uuid4().hex[:32])
        log.error("block_id : %s" , block_id)
        location = course_key.make_usage_key(block_type, block_id)
        log.error("location is : %s", location)
        xblock_class = self.runtime.load_block_type(block_type)
        scope = ScopeIds(self.runtime.user_id, block_type, location, location)
        new_xblock = self.runtime.modulestore.create_child(self.runtime.user_id, self.scope_ids.usage_id , 'tb-fancy' , block_id, fields={'question':'I am Tam'})
        #new_xblock = self.runtime.construct_xblock_from_class(
        #             xblock_class,
                     # We're loading a descriptor, so student_id is meaningless
                     # We also don't have separate notions of definition and usage ids yet,
                     # so we use the location for both.
        #             ScopeIds(self.runtime.user_id, block_type, location, location),
        #             for_parent = self)
        log.error("new xblock usage id  is : %s", new_xblock.scope_ids.usage_id)
        log.error("new xblock object is: %s", new_xblock)
    
        #log.error("the parent xblock i: %s", self)
        #setattr(new_xblock,'question','agkajdlka')
        #new_xblock.save()
        #new_xblock = self.runtime.modulestore.update_item(new_xblock, self.runtime.user_id, allow_not_found=True)
        #log.error("new xblock object after updating parent is: %s", new_xblock)
    
        #self.children.append(new_xblock.location)
        #self.runtime.modulestore.update_item(self, self.runtime.user_id, child_update=True)
        local_context = context.copy()
        local_context['author_edit_view'] = True
        #log.error("scopeid is : %s", self.scope_ids)
        #fragment = super(TemplateBlock, self).author_edit_view(local_context)
        #log.error("okay 000: %s ", self)
        #xml = 'tb-fancy'
        #root = etree.Element(xml)
        #log.error("okay 111: %s", root.tag)
        #usage_id = self.runtime.add_node_as_child(self, root, id_generator=None)
        #new_xblock = self.runtime.modulestore.create_child(self.runtime.user_id, self.scope_ids.usage_id, 'tb-fancy')
        #log.error("okay 222 %s", new_xblock)
        #usage_id = new_xblock.scope_ids.usage_id
        #log.error("okay 333 %s", self.scope_ids.usage_id)
        #log.error("okay 444 %s", self.runtime.descriptor_runtime.id_manager)
        #for child_id in self.children:
        #    child_block = self.runtime.get_block(child_id)
        #    def_id = child_block.runtime.id_reader.get_definition_id(child_id)
        #    type_name = child_block.runtime.id_reader.get_block_type(def_id)
        #    child_class = child_block.runtime.load_block_type(type_name)
        #    log.error("okay 111:  %s", child_block)
        #    log.error("Okay 222: %s %s %s %s %s ",child_block.scope_ids, child_block.scope_ids.usage_id, def_id, type_name, child_class)
        #    setattr(child_block, 'question','alibaba')
            #child_block.force_save_fields(['question'])
        #    log.error("checking field data : %s", child_block)
            #child_block.save()
            #def update_item(self, xblock, user_id, allow_not_found=False, force=False, isPublish=False,
            #                     is_publish_root=True):
        #    self.runtime.modulestore.update_item(child_block, self.runtime.user_id, allow_not_found=True, force=True, isPublish=False, is_publish_root=False)

        #memoryIdManager = MemoryIdManager()
        #parent_id = self.parent
        #parent = self.runtime.get_block(parent_id)
        #self.runtime.id_generator.create_definition('tb-fancy')
        #new_xblock = self.runtime.construct_xblock('tb-fancy', self.scope_ids)
        #new_xblock_id = new_xblock.scope_ids.usage_id
        #log.error("Okay 333 : %s --------- %s", new_xblock_id, new_xblock)
        #new_xblock_id = new_xblock.scope_ids.usage_id
        #updated_new_xblock = self.runtime.get_block(new_xblock_id, self)
        #log.error("okay 3333 %s", updated_new_xblock)
        #self.runtime.add_node_as_child(self, updated_new_xblock, None)
        #log.error("okay 444 %s". updated_new_xblock)
        #new_xblock.parent = self.scope_ids.usage_id
        #new_xblock.save()
        #new_xblock_id = new_xblock.scope_ids.usage_id
        #self.children.append(new_xblock_id)
        #self.save()
        #log.error("okay 444 : %s ---  %s", new_xblock_id, new_xblock)
        for child_id in self.children:
            child_block = self.runtime.get_block(child_id)
            def_id = child_block.runtime.id_reader.get_definition_id(child_id)
            log.error("okay 555:  %s", child_block)
            log.error("Okay 666: %s %s ", child_block.scope_ids.usage_id, def_id)
              

        #def_id = self.runtime.id_generator.create_definition('tb-fancy')
        #usage_id = memoryIdManager.create_usage(def_id)
        #block = self.runtime.get_block(usage_id)
        frag = super(TemplateBlock, self).author_edit_view(local_context)
        #log.error("okay 555 : %s", self.scope_ids.usage_id)
        #local_context = {}
        #if context is None:
        #    local_context = {
        #            'question' : "okay"
        #    }
        #else:
        #        local_context = {
        #            'question' : "not okay"
        #    }
                          
                           
        #frag = Fragment()
                             
        #frag.add_content(loader.render_template('templates/question_template.html', local_context))

        return frag
    def student_view(self, context):
        #frag = Fragment()
        #log.error("okay %s", context)
        #context = {}
        #context = {
        #    "question" : "akjkaljgal"
        #    }
        #log.error("okay 2 %s : ", context)
        #context["question"] = "akakgjda"
        #for child_id in self.children:
        #    child_block = self.runtime.get_block(child_id)
        #    def_id = child_block.runtime.id_reader.get_definition_id(child_id)
        #    type_name = child_block.runtime.id_reader.get_block_type(def_id)
        #    child_class = child_block.runtime.load_block_type(type_name)
        #    fragment = self.runtime.render_child(child_block, view_name="student_view", context=context)
        #    frag.add_frag_resources(fragment)
        #frag.add_frag_resources(self.runtime.render_children(self, view_name="student_view", context=context))
        #return frag
        #def author_preview_view(self, context):
        """
        View for previewing contents in studio.
        """
        children_contents = []
        context = {
            'question' : 'dgjakljdglak'
        }
        
        fragment = Fragment()
        for child_id in self.children:
            child = self.runtime.get_block(child_id)
            child_fragment = self._render_child_fragment(child, context, 'student_view')
            fragment.add_frag_resources(child_fragment)
            children_contents.append(child_fragment.content)
        
        render_context = {
            'block': self,
            'children_contents': children_contents
        }
        render_context.update(context)
        fragment.add_content(self.loader.render_template(self.CHILD_PREVIEW_TEMPLATE, render_context))
        return fragment

       
