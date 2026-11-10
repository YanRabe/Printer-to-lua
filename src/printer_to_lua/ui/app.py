###Imports
from printer_to_lua.data.tooltips import tooltips

#list and dictionaries of general features
from printer_to_lua.data.features import (
                            default_features, features_dict,
                            # start_as_disabled, advanced_features,accel_features,
                            quality_features,
                            materials_features
                            )
from printer_to_lua.data.printer import main_variables, util_functions_text

from pathlib import Path
from typing import cast
from textual.app import App, ComposeResult
from textual import on
from textual.widgets import (
    Header,
    Input,
    Switch,
    Select,
    Button,
    Static,
    TabbedContent,
    TextArea,
)
from textual.reactive import reactive  # ce qui permet de créer des attributs réactifs pour nos classes
from printer_to_lua.ui.state import PrinterUiState
from printer_to_lua.ui.adapter import config_from_widgets
from printer_to_lua.ui.components import FeaturesTab, GeneratedOutput, PrinterEditorTab, ProfileTab
from printer_to_lua.ui.controller import UiController
from printer_to_lua.generators.service import GenerationService
from printer_to_lua.firmware.registry import firmware_ui_templates


###Textual GUI
class gui(App):
    """
    Main class for the GUI. It is launched by the package entry point.
    It is a subclass of the App class from the Textual library.
    Gives access to reactive variables that can change automatically.\n
    Works by yielding predefined widgets to its compose function, for it to "mount it" and display the app in a terminal.
    """

    ENABLE_COMMAND_PALETTE = False
    generation_service = GenerationService()
    controller = UiController()
    ui_state = PrinterUiState()
    # reactive variables. Regularly modified throughout the creation process
    _default_firmware = firmware_ui_templates(0)
    function_dict = _default_firmware.functions

    #dictionaries for each highly conditioned functions. They all have a refresh function that actively changes their content.
    header_dict = _default_firmware.header
    footer_dict = _default_firmware.footer
    select_extruder_dict = _default_firmware.select_extruder
    move_xyz_dict = _default_firmware.move_xyz
    move_xyze_dict = _default_firmware.move_xyze

    featurecode = reactive(                             #Used as a log-text on the right pane
        "Begin by entering your printer's name.",
        always_update=True,
        repaint=True,
        layout=True,
    )  # stores our final result
    printercode = reactive("", always_update=True, repaint=True, layout=True) #same as featurecode but for the printer tab

    extruder_count = reactive(1, always_update=True, repaint=True, layout=True)
    printer_name = reactive("", always_update=True, repaint=True, layout=True)
    firmware = reactive(0, always_update=True, repaint=True, layout=True)
    quality = reactive("low", always_update=True, repaint=True, layout=True)
    material = reactive("pla", always_update=True, repaint=True, layout=True)
    enable_acceleration = reactive(False, always_update=True, repaint=True, layout=True)
    purge_line = reactive(True, always_update=True, repaint=True, layout=True)
    classic_jerk = reactive(False, always_update=True, repaint=True, layout=True)
    heated_chamber = reactive(False, always_update=True, repaint=True, layout=True)
    volumetric_flow = reactive(str(features_dict['additional_features']['volumetric_flow'][0]), 
                               always_update=True, repaint=True, layout=True)
    printing_speed = reactive(str(features_dict['printing_speeds']['print_speed_mm_per_sec'][0]),
                                       always_update=True, repaint=True, layout=True)
    layer_height = reactive(str(features_dict['layer_height']['z_layer_height_mm'][0]), 
                                    always_update=True, repaint=True, layout=True)
    nozzle_diameter = reactive(str(default_features['extruder']['nozzle_diameter_mm_0'][0]), 
                               always_update=True, repaint=True, layout=True)
    
    #custom_features
    auto_bed_leveling = reactive(True, always_update=True, repaint=True, layout=True)
    reload_bed_mesh = reactive(False, always_update=True, repaint=True, layout=True)
    use_per_path_accel = reactive(True, always_update=True, repaint=True, layout=True)

    #reactive variables for the functions in the Printer tab
    craftware_debug = reactive(main_variables["craftware_debug"], always_update=True, repaint=True, layout=True)
    header = reactive("", always_update=True, repaint=True, layout=True)
    footer = reactive("", always_update=True, repaint=True, layout=True)
    comment = reactive(
        function_dict["COMMENT"]["comment"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    layer_start = reactive(
        function_dict["LAYER"]["layer_start"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    layer_stop = reactive(
        function_dict["LAYER"]["layer_stop"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    extruder_start = reactive(
        function_dict["EXTRUDER"]["extruder_start"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    extruder_stop = reactive(
        function_dict["EXTRUDER"]["extruder_stop"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    select_extruder = reactive(
        '',
        always_update=True,
        repaint=True,
        layout=True,
    )
    swap_extruder = reactive(
        function_dict["EXTRUDER"]["swap_extruder"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    prime = reactive(
        function_dict["MOVEMENTS"]["prime"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    retract = reactive(
        function_dict["MOVEMENTS"]["retract"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    move_e = reactive(
        function_dict["MOVEMENTS"]["move_e"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    move_xyz = reactive(
        '',
        always_update=True,
        repaint=True,
        layout=True,
    )
    move_xyze = reactive(
        '',
        always_update=True,
        repaint=True,
        layout=True,
    )
    progress = reactive(
        function_dict["PROGRESS"]["progress"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    set_feedrate = reactive(
        function_dict["SET"]["set_feedrate"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    set_fan_speed = reactive(
        function_dict["SET"]["set_fan_speed"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    set_extruder_temperature = reactive(
        function_dict["SET"]["set_extruder_temperature"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    wait = reactive(
        function_dict["WAIT"]["wait"],
          always_update=True,
          repaint=True,
          layout=True
    )
    set_and_wait_extruder_temperature = reactive(
        function_dict["MIXING PARAMETERS"]["set_and_wait_extruder_temperature"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    set_mixing_ratios = reactive(
        function_dict["MIXING PARAMETERS"]["set_mixing_ratios"],
        always_update=True,
        repaint=True,
        layout=True,
    )
    util_functions = reactive(      #Stores the utility functions
        util_functions_text,
        always_update=True,
        layout=True,
        repaint=True
    )

    TITLE = "Profile to Lua"  # Header's title
    CSS_PATH = (Path(__file__).parent.parent / "assets" / "style.tcss").resolve()

    def compose(self) -> ComposeResult:
        """
        Default and mandatory function used by Textual to compose the app's UI.
        Defined by yielding Widgets from Textual to the console.
        When doing so, the terminal is temporarily inacessible and put in a special mode for Textual to exploit it.
        Every widget is identified by its "id" attribute(str).
        """

        yield Header()  # Ui's header
        with TabbedContent():
            yield FeaturesTab(self.featurecode)

            yield ProfileTab(
                "Quality Profiles",
                "quality_tab",
                "[b]Quality presets",
                "Print quality",
                "quality",
                (("low", "low"), ("medium", "medium"), ("high", "high")),
                quality_features,
                "pq",
                "send-pq",
                "main-text-pq",
                self.featurecode,
            )
            yield ProfileTab(
                "Materials",
                "materials_tab",
                "[b]Materials override",
                "Material",
                "material",
                (("PLA", "PLA"), ("ABS", "ABS"), ("PETG", "PETG")),
                materials_features,
                "pm",
                "send-pm",
                "main-text-pm",
                self.featurecode,
            )

            yield PrinterEditorTab(
                main_variables,
                self.function_dict,
                self.header,
                self.footer,
            )

    @on(Switch.Changed)  # decorator called upon receiving a change in one of the yielded Switch widgets.
    # this decorator declares the following method as a message handler.
    def on_switch_changed(self, event: Switch.Changed) -> None:  # the event class gets the switch's id, value, and more.
        """
        Handles the switch widgets' events.
        """

        if (
            event.switch.id == "add_brim"
        ):  # since "add_brim" is a Switch, its "value" attribute can only be a bool
            if (
                event.switch.value == False
            ):  # if "add brim" is disabled, dependant features will be disabled and
                # output as comments in the lua file (see output handler below).

                self.query("#brim_distance_to_print_mm").first().disabled = (
                    True  # the query('#widget_id') method summons a widget
                )
                # thanks to its id, giving us access to its methods and attributes.
                self.query("#brim_num_contours").first().disabled = True

            else:  # otherwise, toggle them back on and output their values correctly in the lua file.
                self.query("#brim_distance_to_print_mm").first().disabled = False
                self.query("#brim_num_contours").first().disabled = False

        if event.switch.id == 'purge_line':
            self.purge_line = event.value
            self.refresh_header()

        if event.switch.id == "enable_z_lift":  # ditto
            if event.switch.value == False:
                self.query("#extruder_swap_zlift_mm").first().disabled = True
                self.query("#z_lift_mm").first().disabled = True
            else:
                self.query("#z_lift_mm").first().disabled = False
                self.query("#z_lift_mm").first().disabled = False

        if (
            event.switch.id == "enable_acceleration"
        ):  # displays/hides acceleration-related features in advanced mode,
            # and most importantly, entirely disables/enables its handling.
            self.enable_acceleration = event.value
            self.refresh_header()
            self.refresh_footer()

            for feature, enabled in self.controller.acceleration_visibility(event.value).items():
                self.query_one(f"#{feature}").disabled = not enabled
                self.query_one(f"#horizontal_{feature}").display = enabled

        if event.switch.id == "auto_bed_leveling":
            self.auto_bed_leveling = event.value
            self.query('#reload_bed_mesh').first().disabled = not event.value
            self.refresh_header()

        if event.switch.id == "reload_bed_mesh":
            self.reload_bed_mesh = event.value
            self.refresh_header()

        if event.switch.id == 'use_per_path_accel':
            self.use_per_path_accel = event.value
            self.refresh_move_xyz()
            self.refresh_move_xyze()

        if event.switch.id == 'craftware_debug':
            self.craftware_debug = event.value
            self.refresh_move_xyze()

        if (event.switch.id == "advanced_mode"):# toggles advanced mode and displays hidden feature fields.
            for widget_id, visible in self.controller.advanced_visibility(event.value).items():
                self.query_one(f"#{widget_id}").display = visible

        if event.switch.id == "heated_chamber":
            self.heated_chamber = event.value
            self.refresh_header()
            if event.value:
                self.query("#chamber_temp_degree_c").first().disabled = False
                self.query("#chamber_temp_degree_c_min").first().disabled = False
                self.query("#chamber_temp_degree_c_max").first().disabled = False
                self.query("#chamber_temp_degree_c_pm").first().disabled = False
            else:
                self.query("#chamber_temp_degree_c").first().disabled = True
                self.query("#chamber_temp_degree_c_min").first().disabled = True
                self.query("#chamber_temp_degree_c_max").first().disabled = True
                self.query("#chamber_temp_degree_c_pm").first().disabled = True

        if event.switch.id == "enable_fan_pm":
            if event.value:
                self.query("#fan_speed_percent_pm").first().disabled = False
                self.query("#fan_speed_percent_on_bridges_pm").first().disabled = False
            else:
                self.query("#fan_speed_percent_pm").first().disabled = True
                self.query("#fan_speed_percent_on_bridges_pm").first().disabled = True

        if event.switch.id == "classic_jerk":
            self.classic_jerk = event.value
            if event.value:
                self.query("#default_jerk").first().disabled = False
                self.query("#infill_jerk").first().disabled = False

                self.query("#default_junction_deviation").first().disabled = True
                self.query("#perimeter_junction_deviation").first().disabled = True
                self.query("#infill_junction_deviation").first().disabled = True
                self.query("#travel_junction_deviation").first().disabled = True
            else:
                self.query("#default_jerk").first().disabled = True
                self.query("#infill_jerk").first().disabled = True

                self.query("#default_junction_deviation").first().disabled = False
                self.query("#perimeter_junction_deviation").first().disabled = False
                self.query("#infill_junction_deviation").first().disabled = False
                self.query("#travel_junction_deviation").first().disabled = False

        if event.switch.id == 'toggle_code_modification':
            if event.value:
                self.query('#event-text-2').first().disabled = False
            else:
                self.query('#event-text-2').first().disabled = True
    
    
    @on(Select.Changed)  # handles the case of Select widgets being modified.
    def on_select_changed(self, event: Select.Changed) -> None:
        """
        Handles the select widgets' events.
        """
        if not self.is_mounted:
            return

        if (
            event.select.id == "extruder_count"
        ):  # loops through all hidden features describing additional extruders to display/hide them.
            # hidden extruder settings will not be written in the lua output at all, for clarity purposes.
            extruder_count = int(str(event.value))
            for widget_id, visible in self.controller.extruder_visibility(
                extruder_count
            ).items():
                self.query_one(f"#{widget_id}").display = visible

            self.extruder_count = (
                extruder_count
            )  # we store the number of extruders in a reactive variable
            self.refresh_select_extruder()
            # as it will be used for the final output.
            for widget_id, disabled in self.controller.extruder_swap_disabled(
                extruder_count
            ).items():
                self.query_one(f"#{widget_id}").disabled = disabled
        if event.select.id == "bed_circular":  # handles the bed shape.
            # A circular bed (value= True) enables the display of "bed_radius" and deactivates the ability to modify x and y bd sizes
            # as they are defined as 2* the bed_radius
            if event.select.value == False:
                self.query("#bed_radius").first().disabled = True
                self.query("#horizontal_bed_radius").first().display = False

                self.query("#bed_size_x_mm").first().disabled = False
                self.query("#bed_size_y_mm").first().disabled = False
            else:
                self.query("#bed_radius").first().disabled = False
                self.query("#horizontal_bed_radius").first().display = True

                new_radius = float(
                    str(self.query("#bed_radius").first().__getattribute__("value"))
                )
                self.query("#bed_size_x_mm").first().__setattr__(
                    "value", f"{new_radius*2}"
                )
                self.query("#bed_size_y_mm").first().__setattr__(
                    "value", f"{new_radius*2}"
                )

                self.query("#bed_size_x_mm").first().disabled = True
                self.query("#bed_size_y_mm").first().disabled = True

        if event.select.id in [f"nozzle_diameter_mm_{i}" for i in range(self.extruder_count)]:  # minimum and maximum layer thicknesses
            # are rescaled values of the nozzle_diameter.
            values = [float(str(self.query(f"#nozzle_diameter_mm_{i}").first().__getattribute__("value")))
                for i in range(self.extruder_count)]
            
            min_nozzle_diam = min(values)
            max_nozzle_diam = max(values)

            self.query("#z_layer_height_mm_min").first().__setattr__(
                "value", f"{round(min_nozzle_diam*0.1, 2)}"
            )
            self.query("#z_layer_height_mm_max").first().__setattr__(
                "value", f"{round(max_nozzle_diam*0.9, 2)}"
            )
        
        if event.select.id == 'nozzle_diameter_mm_0':
            self.nozzle_diameter = str(event.value)
            self.query('#volumetric_flow').first().__setattr__(
                    'value', f"{round(float(str(event.value))*float(self.layer_height)*float(self.printing_speed), 2)}")

        # firmware selection drastically modifies the generated lua code.
        if event.select.id == "firmware":
            firmware = int(str(event.value))
            self.firmware = firmware
            templates = self.controller.firmware(firmware)
            self.function_dict = templates.functions
            self.header_dict = templates.header
            self.footer_dict = templates.footer
            self.select_extruder_dict = templates.select_extruder
            self.move_xyz_dict = templates.move_xyz
            self.move_xyze_dict = templates.move_xyze

            #other firmwares have different handling of acceleration and jerk settings.
            if (event.value != 0): # if not Marlin
                self.query("#classic_jerk").first().__setattr__("value", True)
                self.query("#classic_jerk").first().disabled = True
                self.query("#default_jerk").first().disabled = False
                self.query("#infill_jerk").first().disabled = False
                self.query("#default_junction_deviation").first().disabled = True
                self.query("#perimeter_junction_deviation").first().disabled = True
                self.query("#infill_junction_deviation").first().disabled = True
                self.query("#travel_junction_deviation").first().disabled = True
            else:
                self.query("#classic_jerk").first().__setattr__("value", False)
                self.query("#classic_jerk").first().disabled = False
                self.query("#default_junction_deviation").first().disabled = False
                self.query("#perimeter_junction_deviation").first().disabled = False
                self.query("#infill_junction_deviation").first().disabled = False
                self.query("#travel_junction_deviation").first().disabled = False

            self.refresh_header()
            self.refresh_footer()
            self.refresh_move_xyz()
            self.refresh_move_xyze()
            self.refresh_select_extruder()

        # default quality values
        if event.select.id == "quality":
            self.quality = event.value
            for widget_id, value in self.controller.quality_defaults(str(event.value)).items():
                setattr(self.query_one(f"#{widget_id}"), "value", value)

        if event.select.id == "material":
            self.material = event.value
            if not self.query("#nozzle_diameter_mm_0_pm"):
                return
            for widget_id, value in self.controller.material_defaults(str(event.value)).items():
                widget = self.query_one(f"#{widget_id}")
                if widget_id == "enable_fan_pm":
                    setattr(widget, "value", value == "true")
                else:
                    setattr(widget, "value", value)
    
    @on(Input.Changed)  # handles the case of input widgets being modified.
    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handles the input widgets' events.
        """
        validation = event.validation_result

        if validation is not None and not validation.is_valid and event.input.id != "name":
                # error log
                self.featurecode = ""
                for error in validation.failure_descriptions or ():
                    self.featurecode += error + "\n"
                self.featurecode += "\nPlease fill in all the fields correctly."
                self.query_one("#main-text", Static).update(self.featurecode)

        if event.input.id == "name":
            self.printer_name = str(event.value)

            if validation is not None and not validation.is_valid:
                # error log
                self.featurecode = ""
                for error in validation.failure_descriptions or ():
                    self.featurecode += error + "\n"
                self.featurecode += "\nName needed to activate other tabs."
                self.query_one("#main-text", Static).update(self.featurecode)

                # disables the other tabs
                self.query("#quality_tab").first().disabled = True
                self.query("#materials_tab").first().disabled = True
                self.query("#send").first().disabled = True
                self.query("#send-printer").first().disabled = True
            else:
                self.featurecode = ""
                self.query_one("#main-text", Static).update(self.featurecode)
                self.query_one("#main-text-pq", Static).update(self.featurecode)
                self.query_one("#main-text-pm", Static).update(self.featurecode)

                self.query("#quality_tab").first().disabled = False
                self.query("#materials_tab").first().disabled = False
                self.query("#send").first().disabled = False
                self.query("#send-printer").first().disabled = False

        if event.input.id == "bed_radius":  # auto rescaling of the bed size values.
            if event.value != "":
                self.query("#bed_size_x_mm").first().__setattr__(
                    "value", f"{float(event.value)*2}"
                )
                self.query("#bed_size_y_mm").first().__setattr__(
                    "value", f"{float(event.value)*2}"
                )

        if event.input.id == "print_speed_mm_per_sec":
            self.printing_speed = event.value
            if event.value != "":
                for widget_id, value in self.controller.speed_defaults(
                    float(event.value),
                    float(self.nozzle_diameter),
                    float(self.layer_height),
                ).items():
                    setattr(self.query_one(f"#{widget_id}"), "value", value)

        if event.input.id == 'z_layer_height_mm':
            self.layer_height = event.value
            self.query('#volumetric_flow').first().__setattr__(
                    'value', f"{round(float(event.value)*float(self.nozzle_diameter)*float(self.printing_speed), 2)}")

        if event.input.id == "default_acc":
            if event.value != "":
                for widget_id, value in self.controller.acceleration_defaults(
                    float(event.value)
                ).items():
                    setattr(self.query_one(f"#{widget_id}"), "value", value)

        if event.input.id == "default_jerk":
            if event.value != "":
                default_accel = float(
                    self.query("#default_acc").first().__getattribute__("value")
                )
                perim_accel = float(
                    self.query("#perimeter_acc").first().__getattribute__("value")
                )
                infill_accel = float(
                    self.query("#infill_acc").first().__getattribute__("value")
                )
                for widget_id, value in self.controller.junction_defaults(
                    event.value,
                    default_accel,
                    perim_accel,
                    infill_accel,
                ).items():
                    setattr(self.query_one(f"#{widget_id}"), "value", value)


    @on(TextArea.Changed)
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """
        Handles the text area widgets' events.        
        """

        if event.text_area.id == "header":
            self.header = event.text_area.text
        
        if event.text_area.id == "footer":
            self.footer = event.text_area.text

        if event.text_area.id == "comment":
            self.comment = event.text_area.text
        
        if event.text_area.id == 'layer_start':
            self.layer_start = event.text_area.text
        
        if event.text_area.id == 'layer_stop':
            self.layer_stop = event.text_area.text
        
        if event.text_area.id == "extruder_start":
            self.extruder_start = event.text_area.text
        
        if event.text_area.id == "extruder_stop":
            self.extruder_stop = event.text_area.text
        
        if event.text_area.id == "select_extruder":
            self.select_extruder = event.text_area.text

        if event.text_area.id == "swap_extruder":
            self.swap_extruder = event.text_area.text
        
        if event.text_area.id == 'prime':
            self.prime = event.text_area.text

        if event.text_area.id == 'retract':
            self.retract = event.text_area.text

        if event.text_area.id == 'move_e':
            self.move_e = event.text_area.text

        if event.text_area.id == "move_xyz":
            self.move_xyz = event.text_area.text

        if event.text_area.id == "move_xyze":
            self.move_xyze = event.text_area.text
        
        if event.text_area.id == "progress":
            self.progress = event.text_area.text
        
        if event.text_area.id == "set_feedrate":
            self.set_feedrate = event.text_area.text
        
        if event.text_area.id == "set_fan_speed":
            self.set_fan_speed = event.text_area.text
        
        if event.text_area.id == "set_extruder_temperature":
            self.set_extruder_temperature = event.text_area.text
        
        if event.text_area.id == "wait":
            self.wait = event.text_area.text
        
        if event.text_area.id == "set_and_wait_temperature":
            self.set_and_wait_extruder_temperature = event.text_area.text
        
        if event.text_area.id == "set_mixing_ratios":
            self.set_mixing_ratios = event.text_area.text
        
        


### Output handler

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Generate one selected artifact through the domain service."""
        button_id = event.button.id
        if not isinstance(button_id, str):
            return
        artifact_by_button = {
            "send": "features",
            "send-pq": "quality",
            "send-pm": "material",
            "send-printer": "printer",
        }
        artifact = artifact_by_button.get(button_id)
        if artifact is None:
            return
        try:
            config = self._config_from_widgets()
            generated = self.generation_service.generate(config)
            self.generation_service.write_artifact(
                Path.cwd(),
                config,
                artifact,
                quality_name=str(self.quality),
                material_name=str(self.material),
            )
            if artifact == "printer":
                self.printercode = generated.printer
                self.query_one("#main-text", GeneratedOutput).set_content(
                    self.printercode
                )
            else:
                content = {
                    "features": generated.features,
                    "quality": generated.quality,
                    "material": generated.material,
                }[artifact]
                self.featurecode = content
                output_id = {
                    "features": "#main-text",
                    "quality": "#main-text-pq",
                    "material": "#main-text-pm",
                }[artifact]
                self.query_one(output_id, GeneratedOutput).set_content(content)
        except (ValueError, OSError) as error:
            message = f"Generation failed: {error}"
            self.featurecode = message
            self.query_one("#main-text", GeneratedOutput).set_content(message)
            self.notify(message, severity="error")

    def _config_from_widgets(self):
        """Snapshot the current controls for the generation service."""
        switches = {
            widget_id: self.query_one(f"#{widget_id}", Switch).value
            for widget_id in (
                "enable_acceleration",
                "classic_jerk",
                "heated_chamber",
                "purge_line",
                "auto_bed_leveling",
                "reload_bed_mesh",
                "use_per_path_accel",
                "craftware_debug",
            )
        }
        function_ids = tuple(
            function
            for category in self.function_dict.values()
            for function in category
        )
        return config_from_widgets(
            self.query_one,
            name=self.printer_name,
            firmware=int(str(self.firmware)),
            extruder_count=int(str(self.extruder_count)),
            switches=switches,
            function_ids=function_ids,
        )

###lua code refreshers
    def refresh_header(self) -> None:
        """
        function to refresh the header of the printer.lua file.
        """
        
        self._refresh_dynamic_sections()
        self.query("#header").first().__setattr__("text", self.header)


    def refresh_footer(self) -> None:
        """
        function to refresh the footer of the printer.lua file.
        """

        self._refresh_dynamic_sections()
        self.query("#footer").first().__setattr__("text", self.footer)


    def refresh_select_extruder(self) -> None:
        """
        function to refresh the select_extruder function of the printer.lua file.
        """

        self._refresh_dynamic_sections()
        self.query("#select_extruder").first().__setattr__("text", self.select_extruder)


    def refresh_move_xyz(self) -> None:
        """
        function to refresh the move_xyz function of the printer.lua file.
        """

        self._refresh_dynamic_sections()
        self.query("#move_xyz").first().__setattr__("text", self.move_xyz)


    def refresh_move_xyze(self) -> None:
        """
        function to refresh the move_xyze function of the printer.lua file.
        """

        self._refresh_dynamic_sections()
        self.query("#move_xyze").first().__setattr__("text", self.move_xyze)

    def _refresh_dynamic_sections(self) -> None:
        """Project reactive app values into the extracted UI state."""
        self.ui_state.firmware = cast(int, self.firmware)
        self.ui_state.extruder_count = cast(int, self.extruder_count)
        self.ui_state.enable_acceleration = self.enable_acceleration
        self.ui_state.classic_jerk = self.classic_jerk
        self.ui_state.heated_chamber = self.heated_chamber
        self.ui_state.purge_line = self.purge_line
        self.ui_state.auto_bed_leveling = self.auto_bed_leveling
        self.ui_state.reload_bed_mesh = self.reload_bed_mesh
        self.ui_state.use_per_path_accel = self.use_per_path_accel
        self.ui_state.craftware_debug = self.craftware_debug
        sections = self.ui_state.render_sections(self.header_dict | self.footer_dict | self.select_extruder_dict | self.move_xyz_dict | self.move_xyze_dict)
        self.header = sections["header"]
        self.footer = sections["footer"]
        self.select_extruder = sections["select_extruder"]
        self.move_xyz = sections["move_xyz"]
        self.move_xyze = sections["move_xyze"]
    
    
    
    def on_mount(self) -> None:
        """
        Mounts the app.
        Adds the tooltips to the widgets.
        Initializes the header, footer, select_extruder, move_xyz and move_xyze.
        """

        self.ui_state = PrinterUiState()
        self.screen.styles.background = "#E8E9F3"  # type: ignore

        # Tooltips:
        for key in tooltips:
            self.query(f"#{key}").first().tooltip = tooltips[key]

        self.refresh_header()
        self.refresh_footer()
        self.refresh_select_extruder()
        self.refresh_move_xyz()
        self.refresh_move_xyze()


def isNotSpaces(text: str):
    """
    Additional function to check if a text is not only spaces.
    """

    return not (text.strip() == "")


if __name__ == "__main__":
    app = gui()
    app.run()
