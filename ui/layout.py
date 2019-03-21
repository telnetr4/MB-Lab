import bpy
import logging
import sys
from .. import algorithms, utils
from .. import settings as s

logger = logging.getLogger(__name__)

gui_status = "NEW_SESSION"
gui_err_msg = ""
gui_active_panel = None
gui_active_panel_fin = None


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    try:
        mb_version = sys.modules['MB-Lab'].bl_info.get('version')
    except AttributeError:
        # needed as the first time draw is run, MB-Lab's bl_info may be undefined.
        # Should update before the user can see it.
        mb_version = (-1, -1, -1)

    bl_label = "MB-Lab {0}.{1}.{2}".format(mb_version[0], mb_version[1], mb_version[2])
    bl_idname = "OBJECT_PT_characters01"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'objectmode'
    bl_category = "MB-Lab"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def draw(self, context):

        global mblab_humanoid, gui_status, gui_err_msg, gui_active_panel
        scn = bpy.context.scene
        icon_expand = "DISCLOSURE_TRI_RIGHT"
        icon_collapse = "DISCLOSURE_TRI_DOWN"

        if gui_status == "ERROR_SESSION":
            box = self.layout.box()
            box.label(text=gui_err_msg, icon="INFO")

        if gui_status == "NEW_SESSION":
            # box = self.layout.box()

            self.layout.label(text="https://github.com/animate1978/MB-Lab")
            self.layout.label(text="CREATION TOOLS")
            self.layout.prop(scn, 'mblab_character_name')

            if mblab_humanoid.is_ik_rig_available(scn.mblab_character_name):
                self.layout.prop(scn, 'mblab_use_ik')
            if mblab_humanoid.is_muscle_rig_available(scn.mblab_character_name):
                self.layout.prop(scn, 'mblab_use_muscle')

            self.layout.prop(scn, 'mblab_use_cycles')
            self.layout.prop(scn, 'mblab_use_eevee')
            if scn.mblab_use_cycles or scn.mblab_use_eevee:
                self.layout.prop(scn, 'mblab_use_lamps')
            self.layout.operator('mbast.init_character')

        if gui_status != "ACTIVE_SESSION":
            self.layout.label(text=" ")
            self.layout.label(text="AFTER-CREATION TOOLS")

            # face rig button
            self.layout.operator('mbast.create_face_rig')
            self.layout.operator('mbast.delete_face_rig')

            if gui_active_panel_fin != "assets":
                self.layout.operator('mbast.button_assets_on', icon=icon_expand)
            else:
                self.layout.operator('mbast.button_assets_off', icon=icon_collapse)
                # assets_status = mblab_proxy.validate_assets_fitting()
                box = self.layout.box()

                box.prop(scn, 'mblab_proxy_library')
                box.prop(scn, 'mblab_assets_models')
                # box.operator('mbast.load_assets_element')
                box.label(text="To adapt the asset, use the proxy fitting tool", icon='INFO')

            if gui_active_panel_fin != "pose":
                self.layout.operator('mbast.button_pose_on', icon=icon_expand)
            else:
                self.layout.operator('mbast.button_pose_off', icon=icon_collapse)
                box = self.layout.box()

                armature = utils.get_active_armature()
                if armature is not None and not utils.is_ik_armature(armature):
                    box.enabled = True
                    sel_gender = algorithms.get_selected_gender()
                    if sel_gender == "FEMALE":
                        if mblab_retarget.femaleposes_exist:
                            box.prop(armature, "female_pose")
                    if sel_gender == "MALE":
                        if mblab_retarget.maleposes_exist:
                            box.prop(armature, "male_pose")
                    box.operator("mbast.pose_load", icon='IMPORT')
                    box.operator("mbast.pose_save", icon='EXPORT')
                    box.operator("mbast.pose_reset", icon='ARMATURE_DATA')
                    box.operator("mbast.load_animation", icon='IMPORT')
                else:
                    box.enabled = False
                    box.label(text="Please select the lab character (IK not supported)", icon='INFO')

            if gui_active_panel_fin != "expressions":
                self.layout.operator('mbast.button_expressions_on', icon=icon_expand)
            else:
                self.layout.operator('mbast.button_expressions_off', icon=icon_collapse)
                box = self.layout.box()
                mblab_shapekeys.update_expressions_data()
                if mblab_shapekeys.model_type != "NONE":
                    box.enabled = True
                    box.prop(scn, 'mblab_expression_filter')
                    box.operator("mbast.keyframe_expression", icon="ACTION")
                    if mblab_shapekeys.expressions_data:
                        obj = algorithms.get_active_body()
                        for expr_name in sorted(mblab_shapekeys.expressions_data.keys()):
                            if hasattr(obj, expr_name):
                                if scn.mblab_expression_filter in expr_name:
                                    box.prop(obj, expr_name)
                    box.operator("mbast.reset_expression", icon="RECOVER_LAST")
                else:
                    box.enabled = False
                    box.label(text="No express. shapekeys", icon='INFO')

            if gui_active_panel_fin != "proxy_fit":
                self.layout.operator('mbast.button_proxy_fit_on', icon=icon_expand)
            else:
                self.layout.operator('mbast.button_proxy_fit_off', icon=icon_collapse)
                fitting_status, proxy_obj, reference_obj = mblab_proxy.get_proxy_fitting_ingredients()

                box = self.layout.box()
                box.label(text="PROXY FITTING")
                box.label(text="Please select character and proxy:")
                box.prop(scn, 'mblab_fitref_name')
                box.prop(scn, 'mblab_proxy_name')
                if fitting_status == "NO_REFERENCE":
                    # box.enabled = False
                    box.label(text="Character not valid.", icon="ERROR")
                    box.label(text="Possible reasons:")
                    box.label(text="- Character created with a different lab version")
                    box.label(text="- Character topology altered by custom modelling")
                    box.label(text="- Character topology altered by modifiers (decimator,subsurf, etc..)")
                if fitting_status == "SAME_OBJECTS":
                    box.label(text="Proxy and character cannot be the same object", icon="ERROR")
                if fitting_status == "CHARACTER_NOT_FOUND":
                    box.label(text="Character not found", icon="ERROR")
                if fitting_status == "PROXY_NOT_FOUND":
                    box.label(text="Proxy not found", icon="ERROR")
                if fitting_status == 'OK':
                    box.label(text="The proxy is ready for fitting.", icon="INFO")
                    proxy_compatib = mblab_proxy.validate_assets_compatibility(proxy_obj, reference_obj)

                    if proxy_compatib == "WARNING":
                        box.label(text="The proxy seems not designed for the selected character.", icon="ERROR")

                    box.prop(scn, 'mblab_proxy_offset')
                    box.prop(scn, 'mblab_proxy_threshold')
                    box.prop(scn, 'mblab_add_mask_group')
                    box.prop(scn, 'mblab_transfer_proxy_weights')
                    box.operator("mbast.proxy_fit", icon="MOD_CLOTH")
                    box.operator("mbast.proxy_removefit", icon="MOD_CLOTH")
                if fitting_status == 'WRONG_SELECTION':
                    box.enabled = False
                    box.label(text="Please select only two objects: humanoid and proxy", icon="INFO")
                if fitting_status == 'NO_REFERENCE_SELECTED':
                    box.enabled = False
                    box.label(text="No valid humanoid template selected", icon="INFO")
                if fitting_status == 'NO_MESH_SELECTED':
                    box.enabled = False
                    box.label(text="Selected proxy is not a mesh", icon="INFO")

            if gui_active_panel_fin != "utilities":
                self.layout.operator('mbast.button_utilities_on', icon=icon_expand)
            else:
                self.layout.operator('mbast.button_utilities_off', icon=icon_collapse)

                box = self.layout.box()
                box.label(text="Choose a proxy reference")
                box.prop(scn, 'mblab_template_name')
                box.operator('mbast.load_base_template')

                box = self.layout.box()
                box.label(text="Bones rot. offset")
                box.operator('mbast.button_adjustrotation', icon='BONE_DATA')
                mblab_retarget.check_correction_sync()
                if mblab_retarget.is_animated_bone == "VALID_BONE":
                    if mblab_retarget.correction_is_sync:
                        box.prop(scn, 'mblab_rot_offset_0')
                        box.prop(scn, 'mblab_rot_offset_1')
                        box.prop(scn, 'mblab_rot_offset_2')
                else:
                    box.label(text=mblab_retarget.is_animated_bone)

        if gui_status == "ACTIVE_SESSION":
            obj = mblab_humanoid.get_object()
            armature = mblab_humanoid.get_armature()
            if obj and armature:
                # box = self.layout.box()

                if mblab_humanoid.exists_transform_database():
                    self.layout.label(text="CREATION TOOLS")
                    x_age = getattr(obj, 'character_age', 0)
                    x_mass = getattr(obj, 'character_mass', 0)
                    x_tone = getattr(obj, 'character_tone', 0)
                    age_lbl = round((15.5 * x_age ** 2) + 31 * x_age + 33)
                    mass_lbl = round(50 * (x_mass + 1))
                    tone_lbl = round(50 * (x_tone + 1))
                    lbl_text = "Age: {0}y  Mass: {1}%  Tone: {2}% ".format(age_lbl, mass_lbl, tone_lbl)
                    self.layout.label(text=lbl_text, icon="RNA")
                    for meta_data_prop in sorted(mblab_humanoid.character_metaproperties.keys()):
                        if "last" not in meta_data_prop:
                            self.layout.prop(obj, meta_data_prop)
                    self.layout.operator("mbast.reset_allproperties", icon="RECOVER_LAST")
                    if mblab_humanoid.get_subd_visibility() == True:
                        self.layout.label(
                            text="Tip: for slow PC, disable the subdivision in Display Options below", icon='INFO')

                if gui_active_panel != "library":
                    self.layout.operator('mbast.button_library_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_library_off', icon=icon_collapse)
                    box = self.layout.box()

                    box.label(text="Characters library")
                    if mblab_humanoid.exists_preset_database():
                        box.prop(obj, "preset")
                    if mblab_humanoid.exists_phenotype_database():
                        box.prop(obj, "ethnic")
                    box.prop(scn, 'mblab_mix_characters')

                if gui_active_panel != "random":
                    self.layout.operator('mbast.button_random_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_random_off', icon=icon_collapse)

                    box = self.layout.box()
                    box.prop(scn, "mblab_random_engine")
                    box.prop(scn, "mblab_set_tone_and_mass")
                    if scn.mblab_set_tone_and_mass:
                        box.prop(scn, "mblab_body_mass")
                        box.prop(scn, "mblab_body_tone")

                    box.label(text="Preserve:")
                    box.prop(scn, "mblab_preserve_mass")
                    box.prop(scn, "mblab_preserve_height")
                    box.prop(scn, "mblab_preserve_tone")
                    box.prop(scn, "mblab_preserve_body")
                    box.prop(scn, "mblab_preserve_face")
                    box.prop(scn, "mblab_preserve_phenotype")
                    box.prop(scn, "mblab_preserve_fantasy")

                    box.operator('mbast.character_generator', icon="FILE_REFRESH")

                if gui_active_panel != "parameters":
                    self.layout.operator('mbast.button_parameters_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_parameters_off', icon=icon_collapse)

                    box = self.layout.box()
                    mblab_humanoid.bodydata_realtime_activated = True
                    if mblab_humanoid.exists_measure_database():
                        box.prop(scn, 'mblab_show_measures')
                    split = box.split()

                    col = split.column()
                    col.label(text="PARAMETERS")
                    col.prop(scn, "morphingCategory")

                    for prop in mblab_humanoid.get_properties_in_category(scn.morphingCategory):
                        if hasattr(obj, prop):
                            col.prop(obj, prop)

                    if mblab_humanoid.exists_measure_database() and scn.mblab_show_measures:
                        col = split.column()
                        col.label(text="DIMENSIONS")
                        col.label(text="Experimental feature", icon='ERROR')
                        col.prop(obj, 'mblab_use_inch')
                        col.prop(scn, 'mblab_measure_filter')
                        col.operator("mbast.measures_apply")

                        if obj.mblab_use_inch:
                            a_inch = getattr(obj, "body_height_Z", 0)
                            m_feet = int(a_inch / 12)
                            m_inch = int(a_inch % 12)
                            col.label(text="Height: {0}ft {1}in ({2}in)".format(m_feet, m_inch, round(a_inch, 3)))
                        else:
                            col.label(text="Height: {0} cm".format(round(getattr(obj, "body_height_Z", 0), 3)))
                        for measure in sorted(mblab_humanoid.measures.keys()):
                            if measure != "body_height_Z":
                                if hasattr(obj, measure):
                                    if scn.mblab_measure_filter in measure:
                                        col.prop(obj, measure)

                        col.operator("mbast.export_measures", icon='EXPORT')
                        col.operator("mbast.import_measures", icon='IMPORT')

                    sub = box.box()
                    sub.label(text="RESET")
                    sub.operator("mbast.reset_categoryonly")

                if mblab_humanoid.exists_measure_database():
                    if gui_active_panel != "automodelling":
                        self.layout.operator('mbast.button_automodelling_on', icon=icon_expand)
                    else:
                        self.layout.operator('mbast.button_automodelling_off', icon=icon_collapse)
                        box = self.layout.box()
                        box.operator("mbast.auto_modelling")
                        box.operator("mbast.auto_modelling_mix")
                else:
                    box = self.layout.box()
                    box.enabled = False
                    box.label(text="Automodelling not available for this character", icon='INFO')

                if mblab_humanoid.exists_rest_poses_database():
                    if gui_active_panel != "rest_pose":
                        self.layout.operator('mbast.button_rest_pose_on', icon=icon_expand)
                    else:
                        self.layout.operator('mbast.button_rest_pose_off', icon=icon_collapse)
                        box = self.layout.box()

                        if utils.is_ik_armature(armature):
                            box.enabled = False
                            box.label(text="Rest poses are not available for IK armatures", icon='INFO')
                        else:
                            box.enabled = True
                            box.prop(armature, "rest_pose")

                            box.operator("mbast.restpose_load")
                            box.operator("mbast.restpose_save")

                if gui_active_panel != "skin":
                    self.layout.operator('mbast.button_skin_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_skin_off', icon=icon_collapse)

                    box = self.layout.box()
                    box.enabled = True
                    if scn.render.engine != 'CYCLES' and scn.render.engine != 'BLENDER_EEVEE':
                        box.enabled = False
                        box.label(text="Skin editor requires Cycles or EEVEE", icon='INFO')

                    if mblab_humanoid.exists_displace_texture():
                        box.operator("mbast.skindisplace_calculate")
                        box.label(text="You need to enable subdiv and displ to see the displ in viewport", icon='INFO')

                    for material_data_prop in sorted(mblab_humanoid.character_material_properties.keys()):
                        box.prop(obj, material_data_prop)

                if gui_active_panel != "file":
                    self.layout.operator('mbast.button_file_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_file_off', icon=icon_collapse)
                    box = self.layout.box()
                    box.prop(scn, 'mblab_show_texture_load_save')
                    if scn.mblab_show_texture_load_save:

                        if mblab_humanoid.exists_dermal_texture():
                            sub = box.box()
                            sub.label(text="Dermal texture")
                            sub.operator("mbast.export_dermimage", icon='EXPORT')
                            sub.operator("mbast.import_dermal", icon='IMPORT')

                        if mblab_humanoid.exists_displace_texture():
                            sub = box.box()
                            sub.label(text="Displacement texture")
                            sub.operator("mbast.export_dispimage", icon='EXPORT')
                            sub.operator("mbast.import_displacement", icon='IMPORT')

                        sub = box.box()
                        sub.label(text="Export all images used in skin shader")
                        sub.operator("mbast.export_allimages", icon='EXPORT')
                    box.prop(scn, 'mblab_export_proportions')
                    box.prop(scn, 'mblab_export_materials')
                    box.operator("mbast.export_character", icon='EXPORT')
                    box.operator("mbast.import_character", icon='IMPORT')

                if gui_active_panel != "finalize":
                    self.layout.operator('mbast.button_finalize_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_finalize_off', icon=icon_collapse)
                    box = self.layout.box()
                    box.prop(scn, 'mblab_save_images_and_backup')
                    box.prop(scn, 'mblab_remove_all_modifiers')
                    box.prop(scn, 'mblab_final_prefix')
                    if scn.mblab_save_images_and_backup:
                        box.operator("mbast.finalize_character_and_images", icon='FREEZE')
                    else:
                        box.operator("mbast.finalize_character", icon='FREEZE')

                if gui_active_panel != "display_opt":
                    self.layout.operator('mbast.button_display_on', icon=icon_expand)
                else:
                    self.layout.operator('mbast.button_display_off', icon=icon_collapse)
                    box = self.layout.box()

                    if mblab_humanoid.exists_displace_texture():
                        if mblab_humanoid.get_disp_visibility() == False:
                            box.operator("mbast.displacement_enable", icon='MOD_DISPLACE')
                        else:
                            box.operator("mbast.displacement_disable", icon='X')
                    if mblab_humanoid.get_subd_visibility() == False:
                        box.operator("mbast.subdivision_enable", icon='MOD_SUBSURF')
                        box.label(text="Subd. preview is very CPU intensive", icon='INFO')
                    else:
                        box.operator("mbast.subdivision_disable", icon='X')
                        box.label(text="Disable subdivision to increase the performance", icon='ERROR')
                    if mblab_humanoid.get_smooth_visibility() == False:
                        box.operator("mbast.corrective_enable", icon='MOD_SMOOTH')
                    else:
                        box.operator("mbast.corrective_disable", icon='X')

                self.layout.label(text=" ")
                self.layout.label(text="AFTER-CREATION TOOLS")
                self.layout.label(
                    text="After-creation tools (expressions, poses, ecc..) not available for unfinalized characters",
                    icon="INFO")

            else:
                gui_status = "NEW_SESSION"
