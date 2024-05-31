###Imports
from datetime import datetime
from pathlib import Path
from tree_sitter_languages import get_language, get_parser
import os
from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Header, Input, Switch, Select, Button, Static, TabbedContent, TabPane, TextArea
from textual.containers import Container, Horizontal, VerticalScroll
from textual.reactive import reactive #ce qui permet de créer des attributs réactifs pour nos classes
from textual.validation import Function

###Features data

#dictionary for basic infos on the printer
default_features = {
"build_area_dimensions" : {
                "bed_circular": False,
                'bed_radius': 155,
                "bed_size_x_mm": 310 ,
                "bed_size_y_mm": 310,
                "bed_size_z_mm": 340},

'printer_extruder' : {
                "extruder_count": 1,
                "nozzle_diameter_mm_0": 0.4,
                "filament_diameter_mm_0": 1.75,
                "filament_linear_adv_factor": 0.06}
}

#intermediate variables used to define features rescaled from others
default_printing_speed = 60
default_jerk = 20
default_accel = 3000

#main dictionary with every feature needed to print, at least for most printers.
features_dict = {
'retraction_settings' : {
                "filament_priming_mm": 0.8,
                "priming_mm_per_sec": 25,
                "retract_mm_per_sec":25},

'layer_height': {
                "z_layer_height_mm": 0.2,
                "z_layer_height_mm_min": round(default_features["printer_extruder"]['nozzle_diameter_mm_0']*0.10, 2),
                "z_layer_height_mm_max":round(default_features["printer_extruder"]['nozzle_diameter_mm_0']*0.80, 2)},

'printing_temperatures' : {
                "extruder_temp_degree_c": 210,
                "extruder_temp_degree_c_min":150,
                "extruder_temp_degree_c_max":250,

                "bed_temp_degree_c":60,
                "bed_temp_degree_c_min":0,
                "bed_temp_degree_c_max":120,
                
                "heated_chamber": False,
                "chamber_temp_degree_c": 0,
                "chamber_temp_degree_c_min": 0,
                "chamber_temp_degree_c_max": 110},

'printing_speeds' : {
                "print_speed_mm_per_sec": default_printing_speed,
                "print_speed_mm_per_sec_min":default_printing_speed/3,
                "print_speed_mm_per_sec_max": default_printing_speed*3.5,

                "perimeter_print_speed_mm_per_sec": default_printing_speed*0.75,
                "perimeter_print_speed_mm_per_sec_min": default_printing_speed/3,
                "perimeter_print_speed_mm_per_sec_max": default_printing_speed*2.8,

                "cover_print_speed_mm_per_sec": default_printing_speed*0.75,
                "cover_print_speed_mm_per_sec_min": default_printing_speed/3,
                "cover_print_speed_mm_per_sec_max": default_printing_speed*2.8,

                "first_layer_print_speed_mm_per_sec":  default_printing_speed/3,
                "first_layer_print_speed_mm_per_sec_min": 5,
                "first_layer_print_speed_mm_per_sec_max": default_printing_speed*2.8,

                "travel_speed_mm_per_sec": default_printing_speed*3,
                "travel_speed_mm_per_sec_min":50,
                "travel_speed_mm_per_sec_max": 500},

'acceleration_settings' : {
                "x_max_speed": 500,
                "y_max_speed":500,
                "z_max_speed":30,
                "e_max_speed":100,

                "default_acc":default_accel,
                "e_prime_max_acc":default_accel/2,
                "perimeter_acc":default_accel/2,
                "infill_acc":default_accel,

                "x_max_acc":default_accel,
                "y_max_acc":default_accel,
                "z_max_acc":default_accel/40,
                "e_max_acc":default_accel,

                "classic_jerk": False,
                "default_jerk":default_jerk,
                "infill_jerk":default_jerk,
                "default_junction_deviation": round(0.4*(default_jerk**2/default_accel),4),
                "perimeter_junction_deviation": round(0.4*(default_jerk**2/default_accel),4),
                "infill_junction_deviation": round(0.4*(default_jerk**2/default_accel),4),
                "travel_junction_deviation":round(0.4*(default_jerk**2/default_accel), 4),
                },

'misc_default_settings' : {

                "enable_active_temperature_control": True,
                "add_brim": True,
                "brim_distance_to_print_mm":2,
                "brim_num_contours": 3,
                "enable_z_lift": True,
                "z_lift_mm":1,
                "enable_travel_straight":True,

                
                "extruder_swap_zlift_mm": 0.2,
                "extruder_swap_retract_length_mm": 6.5,
                "extruder_swap_retract_speed_mm_per_sec": 25
                },

"additional_features":{
                "use_per_path_accel": False,
                "volumetric_flow": 10,
                "reload_bed_mesh": False,
                "auto_bed_leveling": False,
                }
}

quality_features = {
    'layer_thickness_changes':{
        'z_layer_height_mm': 0.2
    },

    'speed_changes':{
        'print_speed_mm_per_sec': 60,
        'perimeter_print_speed_mm_per_sec': 30,
        'cover_print_speed_mm_per_sec': 30,
        'first_layer_print_speed_mm_per_sec': 20,
        'travel_speed_mm_per_sec': 80,
        'priming_mm_per_sec': 40,
        'retract_mm_per_sec': 40,
        'speed_multiplier_0': 1
    }
}


materials_features = { 

    'retraction_changes': {
        'filament_priming_mm': 0.8,
    },

    'temperature_changes':{
        'extruder_temp_degree_c':210,
        'bed_temp_degree_c': 60,
        'chamber_temp_degree_c': 0,
        'enable_fan': True,
        'fan_speed_percent': 100,
        'fan_speed_percent_on_bridges': 100
    },

    'speed_changes': {
        'print_speed_mm_per_sec': 60,
        'perimeter_print_speed_mm_per_sec': 45,
        'cover_print_speed_mm_per_sec': 30,
        'first_layer_print_speed_mm_per_sec': 20,
    }
}


tooltips = {
    'static_firmware': "Defines G-code flavor. Entirely defines your printer's behaviour and the way your 3d model is translated to G-code instructions understandable by the machine. ",
    'static_advanced_mode': 'Toggle to hide/display advanced features. Please note they are mostly assigned according to parent-features, thus modifying them may yield unexpected results.',
    'static_build_area_dimensions': "Settings defining your printer's bed",
    'static_bed_circular': "Defines your bed's shape; it can either be rectangular or circular. \n Having a circular bed means the size parameters are solely defined by the bed's radius.",
    'static_bed_radius': "If circular, defines your bed's radius and thus, its size-parameters.",
    'static_bed_size_x_mm': "Your bed's length (mm)",
    'static_bed_size_y_mm': "Your bed's width (mm)",
    'static_bed_size_z_mm': "Your bed's height (mm)",
    'static_extruder_settings': "Settings defining your extruder(s) such as the nozzle diameter.",
    'static_extruder_count': "The number of extruders on your printer.",
    'static_nozzle_diameter_mm_0': "Defines your first extruder's nozzle diameter (mm).",
    'static_filament_diameter_mm_0': "Defines your first extruder's filament diameter (mm).",
    'static_filament_linear_adv_factor': "Linear Advance grants the firmware the ability to predict the pressure build-up in the extruder at higher speed, therefore allowing it to decrease the flow of material to avoid blobs and other artifacts. This parameter defines the k-factor for said decrease.",
    'static_retraction_settings': "Optional and advanced settings. Defines your printer's behaviour when it retracts (z-axis) itself from a print.",
    'static_filament_priming_mm': "Defines the length of the filament retracted to prevent oozing during travel motions.",
    'static_priming_mm_per_sec': "Defines the speed at which the filament is retracted.",
    'static_retract_mm_per_sec': "Defines the speed at which the extruder retracts itself (z-axis) from the current print.",
    'static_layer_height': "Settings defining the thickness of each layer.",
    'static_z_layer_height_mm': "Defines the general thickness of each layer (mm). It is usually used to qualify the print's overall quality with 0.2 being a draft.",
    "static_z_layer_height_mm_min": "Defines the smallest thickness (mm) achievable by the printer. Automatically scaled in accordance to nozzle diameter.",
    "static_z_layer_height_mm_max": "Defines the largest thickness (mm) achievable by the printer. Automatically scaled in accordance to nozzle diameter.",
    "static_printing_temperatures": "Settings defining your printer's default temperatures (C). Highly dependent on the material.",
    "static_extruder_temp_degree_c": "Defines your extruder's temperature. Please refer to your filament's recommendations.",
    "static_extruder_temp_degree_c_min": "Based on the previous setting",
    "static_extruder_temp_degree_c_max": "Based on the previous setting",
    "static_bed_temp_degree_c": "Defines your bed's heating temperature. Heating your bed to the correct temperature is crucial to efficiently deposit the first layer and make sure it sticks to the surface.",
    "static_bed_temp_degree_c_min": "Based on the previous setting.",
    "static_bed_temp_degree_c_max": "Based on the previous setting.",
    "static_printing_speeds": "Settings defining the general speed at which your printer moves its extruder around.",
    "static_print_speed_mm_per_sec": "Defines the general printing speed, meaning the speed at which your nozzle actively extrudes material.",
    "static_print_speed_mm_per_sec_min": "Based on the previous setting.",
    "static_print_speed_mm_per_sec_max": "Based on the previous setting. ",
    "static_perimeter_print_speed_mm_per_sec": "Defines the specific speed at which perimeters are printed. Set by default to 3/4 of the general printing speed.",
    "static_perimeter_print_speed_mm_per_sec_min": "Based on the previous setting.",
    "static_perimeter_print_speed_mm_per_sec_max": "Based on the previous setting.",
    "static_cover_print_speed_mm_per_sec": "Defines the specific speed at which covers are printed. Set by default to 3/4 of the general printing speed.",
    "static_cover_print_speed_mm_per_sec_min": "Based on the previous setting.",
    "static_cover_print_speed_mm_per_sec_max": "Based on the previous setting.",
    "static_first_layer_print_speed_mm_per_sec": "Defines the specific speed at which the very first layer is printed. Set by default to 1/3 of the general printing speed.",
    "static_first_layer_print_speed_mm_per_sec_min": "Based on the previous setting.",
    "static_first_layer_print_speed_mm_per_sec_max": "Based on the previous setting.",
    "static_travel_speed_mm_per_sec": "Defines the general travel speed at which the extruder moves when not printing. Set by default to 3 times the general printing speed.",
    "static_travel_speed_mm_per_sec_min": "Based on the previous setting.",
    "static_travel_speed_mm_per_sec_max": "Based on the previous setting.",
    "static_acceleration_settings": "Optional and advanced settings. Help modify the way the printer handles acceleration.",
    "static_enable_acceleration": "Enable / disable acceleration handling. Highly dependant on the firmware and still experimental. May not work as expected on every printer.",
    "static_x_max_speed": "Maximum speed reachable by the machine on the x-axis. Usually the same as the y-axis.",
    "static_y_max_speed": "Maximum speed reachable by the machine on the y-axis. Usually the same as the x-axis.",
    "static_z_max_speed": "Maximum speed reachable by the machine on the z-axis. Usually way lower that the two previous maximums.",
    "static_e_max_speed": "Maximum speed reachable by the machine idk i'm making things up rn.",
    "static_x_max_acc": "Max acceleration on the x-axis (mm/s^2). By default, set to 'default acceleration's' value.",
    "static_y_max_acc": "Max acceleration on the y-axis (mm/s^2). By default, set to 'default acceleration's' value.",
    "static_z_max_acc": "Max acceleration on the z-axis (mm/s^2). By default, set to 'default acceleration's' value.",
    "static_e_max_acc": "Max acceleration on the e-axis (mm/s^2). By default, set to 'default acceleration's' value.",
    "static_default_acc": "Defines the general acceleration (mm/s^2).",
    "static_e_prime_max_acc": "Defines the acceleration aimed when retracting the filament. Set by default to previous setting's value.",
    "static_perimeter_acc": "Defines the acceleration aimed when printing the perimeter. Set by default to previous setting's value.",
    "static_infill_acc": "Defines the acceleration aimed when printing the infill. Set by default to previous setting's value.",
    "static_default_jerk": "Jerk handles sharp 90-degree edges, by setting the maximum instantaneous change in velocity possible. This setting defines the default value of the printer's jerk.",
    "static_infill_jerk": "Defines jerk value for infills.",
    "static_misc_default_settings": "Miscellaneous settings.",
    "static_add_brim": "A brim is an extension to your print's first layer, deposited before the latter. It serves as a massive adhesion improvement and helps at avoiding warping. This setting toggles the addition of a brim.",
    "static_brim_distance_to_print_mm": "Defines the distance (mm) from your print's base at which the brim is started.",
    "static_brim_num_contours": "Defines the number of contours to your brim. More contours means a larger and more adhesive brim, but eventually makes it harder to take off the bed.",
    "static_enable_z_lift": "Z lift allows the nozzle to lift itself up the z-axis before traveling, thus preventing it from inadvertendly smashing onto your print or dragging it away.",
    "static_z_lift_mm": "Defines the height of the Z lift.",
    "static_enable_travel_straight": "Travel straight lets the extruder get from a point to another without staying inside the print's parameter as it would normally do. This lessens travel distances but may cause defects and artifacts if the filament is not properly retracted.",
}


#list of advanced features that are mostly rescaled values of defining features, hidden by default. 
#Used later to enable/disable their display. 
advanced_features = ["enable_active_temperature_control", 'filament_linear_adv_factor','perimeter_print_speed_mm_per_sec', 'cover_print_speed_mm_per_sec', 
                     "first_layer_print_speed_mm_per_sec", 'travel_speed_mm_per_sec', 'enable_travel_straight'] 
advanced_features += [feature for feature in features_dict["retraction_settings"]] 
advanced_features += [feature for category in features_dict for feature in features_dict[category] if 
                      (feature.endswith('min')or feature.endswith('max') or feature.startswith('extruder_swap'))]
advanced_features += [feature for feature in features_dict['additional_features']]

start_as_disabled = ['default_jerk', 'infill_jerk','chamber_temp_degree_c','chamber_temp_degree_c_min','chamber_temp_degree_c_max']
#list of acceleration features. Hidden by default and only accessible when acceleration is enabled in advanced mode.
accel_features = [feature for feature in features_dict["acceleration_settings"]]

###Printer file

#needed to create a reactive console in lua syntax
# lua_language = get_language("lua")
# lua_highlight_query = (Path(__file__).parent / "lua_highlights.scm").read_text()

# base_code = 'idkdude = 1'
# print(lua_highlight_query)

main_variables = {
    'extruder_e': 0,
    "exruder_e_restart": 0,
    'current_z': 0.0,

    'changed_frate': False,
    'processing': False,

    'current_extruder': 0,
    'current_frate': 0,

    'current_fan_speed': -1,
    'craftware': True
}

#MARLIN

footer = '''
 --called to create the footer of the G-Code file.

output('')
output('G4 ; wait')
output('M104 S0 ; turn off temperature')
output('M140 S0 ; turn off heatbed')
output('M107 ; turn off fan')
output('G28 X Y ; home X and Y axis')
output('G91')
output('G0 Z 10') -- move in Z to clear space between print and nozzle
output('G90')
output('M84 ; disable motors')
output('')

-- restore default accel
output('M201 X' .. x_max_acc .. ' Y' .. y_max_acc .. ' Z' .. z_max_acc .. ' E' .. e_max_acc .. ' ; sets maximum accelerations, mm/sec^2')
output('M203 X' .. x_max_speed .. ' Y' .. y_max_speed .. ' Z' .. z_max_speed .. ' E' .. e_max_speed .. ' ; sets maximum feedrates, mm/sec')
output('M204 P' .. default_acc .. ' R' .. e_prime_max_acc .. ' T' .. default_acc .. ' ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2')
output('M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec')
output('M205 J' .. default_junction_deviation .. ' ; sets Junction Deviation')
'''

comment = ''

layer_start = ''

layer_stop = ''

exruder_start= ''

extruder_stop = ''

select_extruder = ''

swap_extruder = ''

prime = ''

retract = ''

move_e = ''

move_xyz = ''

move_xyze = ''

progress = ''

set_feedrate = ''

set_fan_speed = ''

set_extruder_temperature= ''

wait = ''

set_and_wait_extruder_temperature = ''

set_mixing_ratios = ''

#REPRAP

#KLIPPER

###Textual GUI
class gui(App):
    '''Subclass of Textual's integrated App class.
    Gives access to reactive variables that can change automatically.
    Works by yielding predefined widgets to its compose function, for it to "mount it" and display the app in a terminal.
    '''
    ENABLE_COMMAND_PALETTE = False
    #reactive variables. Regularly modified throughout the creation process
    featurecode = reactive("Begin by entering your printer's name.", always_update=True, repaint=True, layout=True) #stores our final result
    printercode = reactive("", always_update=True, repaint=True, layout=True)
    extrudercount = reactive(1, always_update=True, repaint=True, layout=True)
    printername = reactive('', always_update=True, repaint=True, layout=True)
    quality = reactive('low', always_update=True, repaint=True, layout=True)
    material = reactive('pla', always_update=True, repaint=True, layout=True)
    enableacceleration = reactive(False, always_update=True, repaint=True, layout=True)
    printerheader = reactive('', always_update=True, repaint=True, layout=True)
    printerfooter = reactive('', always_update=True, repaint=True, layout=True)
    classicjerk = reactive(False, always_update=True, repaint=True, layout=True)
    autobedleveling = reactive(False, always_update=True, repaint=True, layout=True)
    reloadbedmesh = reactive(False, always_update=True, repaint=True, layout=True)
    firmware = reactive(0, always_update=True, repaint=True, layout=True)
    heatedchamber = reactive(False, always_update=True, repaint=True, layout=True)
    TITLE = 'Profile to Lua' #Header's title
    CSS_PATH = 'style.tcss' #Graphic elements are managed through tcss files, much like web css.

    def compose(self) -> ComposeResult:
        '''Default and mandatory function used by Textual to compose the app's UI.
        Defined by yielding Widgets from Textual to the console.
        When doing so, the terminal is temporarily inacessible and put in a special mode for Textual to exploit it.
        
        Every widget is identified by its "id" attribute(str).'''

        yield Header() #Ui's header
        with TabbedContent():
            #FEATURES TAB
            with TabPane("Features"):
                with Container(classes="app-grid"): #Overall container. allows for agile widget placements. 
                    #Here, it uses the 'grid' format spanning 3 columns and 1 row.
                    with VerticalScroll(classes="features"): #left side vertical column, containing the feature fields.

                        #Advanced mode label and button
                        yield Horizontal( #Horizontal widgets are solely used to contain other subwidgets, 
                            #and allows to hide/display all of its children at once.
                            Static("[b]Advanced mode", classes="feature-text", id='static_advanced_mode'), #Static widgets define immutable 
                            #renderable objects. mainly used for plain texts
                            Switch(value=False, id ="advanced_mode"), #Switch widgets define a toggle-switch with value False and True in accordance 
                            #to its state.
                            classes="container") #the "classes" attribute is similar to its Web counterpart, refering the css file.
                        
                        #Printer settings
                        yield Static("[b]Printer", classes="label", id='static_printer')

                        yield Horizontal(
                            Static("Printer's name", classes="feature-text", id='static_printer_name'),

                            #Input widgets define an input field.
                            #its "type" attribute allows for active input restriction (either "text", "number", or "integer")
                            #its value is stored in a "value" attribute, 
                            #only accessible through private method "__getattribute__('value')" or publicly through event controls (down below)
                            Input(placeholder="Printer's name", id="printer_name", type="text", max_length=64, valid_empty=False, validators=[Function(isNotSpaces, "empty name")]),

                            classes="horizontal-layout")
                        yield Horizontal(
                            Static("Firmware", classes="feature-text", id='static_firmware'),

                            #Select widgets define a scrollable field.
                            #its "options" attribute define possible choices through the tuple: ("display name", true_value)
                            #getting the "value" of a Select widget grants the "true_value" variable of the active selection.
                            #It is accessible through private method "__getattribute__('value')" or publicly through event controls.
                            Select(id='firmware', prompt= "Firmware", options= [('Marlin', 0), ('Rep Rap', 1), ('Klipper', 2), ('Other', 3)], allow_blank=False), 
                            classes="horizontal-layout"
                        )

                        #Build Area Dimensions
                        yield Static("[b]Build Area Dimensions", classes="label", id='static_build_area_dimensions')

                        yield Horizontal(
                            Static("Bed Shape", classes='feature-text', id='static_bed_circular'),
                            Select(value=False, prompt='bed shape', allow_blank=False, options=[('rectangular', False), ('circular', True)], 
                                id='bed_circular'),
                            classes='container'
                        )
                        bed_radius_input = Input(value = f'{default_features["build_area_dimensions"]["bed_radius"]}',
                                                placeholder="bed radius", id="bed_radius", type="number", max_length=4, 
                                                valid_empty=False)
                        bed_radius_input.disabled = True
                        bed_radius_widget = Horizontal(
                            Static("Bed Radius", classes='feature-text', id='static_bed_radius'),
                            bed_radius_input,
                            classes='horizontal-layout',id='horizontal_bed_radius'
                        )
                        bed_radius_widget.display = False #Hides the widget.
                        yield bed_radius_widget

                        yield Horizontal(
                            Static("Bed Size x (mm)", classes="feature-text", id='static_bed_size_x_mm'), 
                            Input(value = '310',placeholder="bed size x mm ", id="bed_size_x_mm", type="number", 
                                max_length=4, valid_empty=False),
                            classes="horizontal-layout")
                        yield Horizontal(
                            Static("Bed Size y (mm)", classes="feature-text", id='static_bed_size_y_mm'), 
                            Input(value = '310',placeholder="bed size y mm ", id="bed_size_y_mm", type="number", 
                                max_length=4, valid_empty=False),
                            classes="horizontal-layout")
                        yield Horizontal(
                            Static("Bed Size z (mm)", classes="feature-text", id='static_bed_size_z_mm'), 
                            Input(value = '350',placeholder="bed size z mm ", id="bed_size_z_mm", type="number", 
                                max_length=4, valid_empty=False),
                            classes="horizontal-layout")
                        
                        #Printer Extruder
                        yield Static("[b]Extruder Settings", classes="label", id='static_extruder_settings')

                        yield Horizontal(
                            Static("Extruder count", classes="feature-text", id='static_extruder_count'), 
                            Select(prompt="extruder count", id="extruder_count", 
                                options=[(f"{i}", i) for i in range(1, 15)], allow_blank=False),
                            classes="horizontal-layout")
                                        
                        yield Horizontal(
                            Static("Nozzle Diameter (mm)", classes="feature-text", id='static_nozzle_diameter_mm_0'), 
                            Select(value=0.4,prompt="Nozzle diameter (mm)", id="nozzle_diameter_mm_0", 
                                options=[('0.25', 0.25),('0.4', 0.4), ('0.6', 0.6)], allow_blank=False),
                            classes="horizontal-layout")
                            
                        yield Horizontal(
                            Static(f"Filament diameter", classes="feature-text", id='static_filament_diameter_mm_0'),
                            Select(prompt="filament diameter (mm)", id="filament_diameter_mm_0", 
                                options=[('1.75', 1.75),('3.0', 3.0)], allow_blank=False),
                            classes="horizontal-layout")
                        
                        #loop to generate doublons of extruder settings, in case there are more than one. 
                        #maximum number for supported printers is 14 with the Addiform, thus explaining the loop range.
                        for i in range(2, 15):
                            title_nozzle = Static(f"Nozzle Diameter for extruder {i} (mm)", classes="feature-text", 
                                                id=f'static_nozzle_diameter_mm_{i-1}')
                            input_field_nozzle = Select(value = 0.4, prompt=f"Nozzle diameter for extruder {i} (mm)", 
                                                        id=f"nozzle_diameter_mm_{i-1}", options=[('0.25', 0.25),('0.4', 0.4), ('0.6', 0.6)], 
                                                        allow_blank=False)
                            horizontal_nozzle = Horizontal(
                                title_nozzle, 
                                input_field_nozzle,
                                classes="horizontal-layout", id=f'horizontal_nozzle_{i-1}')
                            horizontal_nozzle.display = False
                            yield horizontal_nozzle
                            
                            title_fildiam = Static(f"Filament diameter for extruder {i} (mm)", classes="feature-text", 
                                                id=f'static_filament_diameter_mm_{i-1}')
                            input_field_fildiam = Select(value = 1.75, prompt=f"filament diameter for extruder {i} (mm)", 
                                                        id=f"filament_diameter_mm_{i-1}", options=[('1.75', 1.75),('3.0', 3.0)], 
                                                        allow_blank=False)
                            horizontal_fildiam = Horizontal(
                                title_fildiam, 
                                input_field_fildiam,
                                classes="horizontal-layout", id=f'horizontal_fildiam_{i-1}')
                            horizontal_fildiam.display = False
                            yield horizontal_fildiam

                        fil_adv_fact =  Horizontal(
                            Static("Filament Linear Advance Factor", classes="feature-text", 
                                id='static_filament_linear_adv_factor'), 
                            Input(value = '0.06',placeholder="filament linear advance factor", 
                                id="filament_linear_adv_factor", type="number", max_length=2, valid_empty=False),
                            classes="horizontal-layout", id='horizontal_filament_linear_adv_factor')
                        fil_adv_fact.display = False
                        yield fil_adv_fact
                        
                        #Other parameters. loops through features_dict to create remaining input fields.
                        for category in features_dict: #category is a key
                            tmp_key_words = [word for word in category.split('_')] #List of words in the feature's name. 
                            #Used solely for proper text display purposes
                            placeholder_value = '' #tmp variable used to concatenate the new title altogether.
                            for word in tmp_key_words:
                                placeholder_value += word + ' '
                            title_tmp = Static(f"[b]{placeholder_value.title()}", classes="label", id=f'static_{category}') #.title() built-in 
                            #function uppercases each starting letter.
                            if category != "acceleration_settings": #acceleration settings is a special case as it is shown only after toggling 
                                #"enable acceleration" in advanced mode
                                yield title_tmp
                            else:
                                yield title_tmp
                                #the "enable acceleration toggle-switch"
                                enable_accel = Horizontal(
                                        Static("Enable acceleration", classes='feature-text', id='static_enable_acceleration'),
                                        Switch(value=False, id='enable_acceleration'),
                                        classes='container',
                                        id='horizontal_enable_acceleration'
                                        )
                                enable_accel.display = False
                                yield enable_accel

                            #Loops through each feature in a category
                            for feature in features_dict[category]:#feature is also a key.
                                tmp_feature_words = [word for word in feature.split('_')]
                                placeholder_value = ''
                                for word in tmp_feature_words:
                                    if word in ['mm', 'c'] and feature.endswith(word):#temporary solution to decorate units. 
                                        #Will find better later.
                                        placeholder_value += f'({word})'
                                    else:     
                                        placeholder_value += word + ' '
                                if not isinstance(features_dict[category][feature], bool):#non bool- features will yield an Input widget,
                                    #while bools will yield a Switch
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}')
                                    feature_input_field = Input(value=f'{features_dict[category][feature]}', placeholder=f"{placeholder_value}", 
                                                                id=f"{feature}", type="number", max_length=5, valid_empty=False)
                                    if feature in start_as_disabled:
                                        feature_input_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                                        feature_text,
                                                        feature_input_field,
                                                        classes="horizontal-layout", 
                                                        id=f"horizontal_{feature}")
                                    if feature in advanced_features or feature in accel_features: #features judged too advanced for a beginner 
                                        #are by default hidden
                                        feature_horizontal.display = False
                                    yield feature_horizontal

                                else: #bool features'case
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}')
                                    feature_switch_field = Switch(value=features_dict[category][feature], id =f"{feature}")
                                    if feature in start_as_disabled:
                                        feature_switch_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                        feature_text,
                                        feature_switch_field,
                                        classes="horizontal-layout", id=f"horizontal_{feature}")
                                    if feature in advanced_features or feature in accel_features:
                                        feature_horizontal.display = False
                                    yield feature_horizontal

                        #Create button. Handled solely by its decorated function down below.
                        yield Button("[b]Create", id="send", disabled=True)

                    with VerticalScroll(classes="event-text"):
                        '''Right column. 
                        Used for active debug purposes by showing the Lua output or eventual warnings.'''
                        yield Static(self.featurecode, id='main-text', classes='text')
            

            
            #QUALITY TAB
            with TabPane('Quality Profiles', id='quality_tab') as quality_tab:
                quality_tab.disabled = True
                with Container(classes="app-grid"): #Overall container. allows for agile widget placements. 
                    #Here, it uses the 'grid' format spanning 3 columns and 1 row.
                    with VerticalScroll(classes="features"): #left side vertical column, containing the feature fields.

                        #Printer settings
                        yield Static("[b]Quality presets", classes="label", id='static_quality_presets')

                        yield Horizontal(
                            Static("Print quality", classes="feature-text", id='static_quality_level'),

                            #Input widgets define an input field.
                            #its "type" attribute allows for active input restriction (either "text", "number", or "integer")
                            #its value is stored in a "value" attribute, 
                            #only accessible through private method "__getattribute__('value')" or publicly through event controls (down below)
                            Select(prompt="Print quality", id="quality", options=[('low', 'low'), ('medium', 'medium'), ('high', 'high')], allow_blank=False),
                            classes="horizontal-layout")

                        #Other parameters. loops through quality_features to create remaining input fields.
                        for category in quality_features: #category is a key
                            tmp_key_words = [word for word in category.split('_')] #List of words in the feature's name. 
                            #Used solely for proper text display purposes
                            placeholder_value = '' #tmp variable used to concatenate the new title altogether.
                            for word in tmp_key_words:
                                placeholder_value += word + ' '
                            title_tmp = Static(f"[b]{placeholder_value.title()}", classes="label", id=f'static_{category}_pq') #.title() built-in 
                            #function uppercases each starting letter.
                            yield title_tmp
                        
                            #Loops through each feature in a category
                            for feature in quality_features[category]:#feature is also a key.
                                tmp_feature_words = [word for word in feature.split('_')]
                                placeholder_value = ''
                                for word in tmp_feature_words:
                                    if word in ['mm', 'c'] and feature.endswith(word):#temporary solution to decorate units. 
                                        #Will find better later.
                                        placeholder_value += f'({word})'
                                    else:     
                                        placeholder_value += word + ' '
                                if not isinstance(quality_features[category][feature], bool):#non bool- features will yield an Input widget,
                                    #while bools will yield a Switch
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}_pq')
                                    feature_input_field = Input(value=f'{quality_features[category][feature]}', placeholder=f"{placeholder_value}", 
                                                                id=f"{feature}_pq", type="number", max_length=5, valid_empty=False)
                                    if feature in start_as_disabled:
                                        feature_input_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                                        feature_text,
                                                        feature_input_field,
                                                        classes="horizontal-layout", 
                                                        id=f"horizontal_{feature}_pq")
                                    # if feature in advanced_features: #features judged too advanced for a beginner 
                                    #     #are by default hidden
                                    #     feature_horizontal.display = False
                                    yield feature_horizontal

                                else: #bool features'case
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}_pq')
                                    feature_switch_field = Switch(value=quality_features[category][feature], id =f"{feature}_pq")
                                    if feature in start_as_disabled:
                                        feature_switch_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                        feature_text,
                                        feature_switch_field,
                                        classes="horizontal-layout", id=f"horizontal_{feature}_pq")
                                    # if feature in advanced_features:
                                    #     feature_horizontal.display = False
                                    yield feature_horizontal

                        #Create button. Handled solely by its decorated function down below.
                        yield Button("[b]Create", id="send-pq", disabled=False)
                    
                    
                    with VerticalScroll(classes="event-text"):
                        '''Right column. 
                        Used for active debug purposes by showing the Lua output or eventual warnings.'''
                        yield Static(self.featurecode, id='main-text-pq', classes='text')



            #MATERIALS TAB
            with TabPane("Materials", id='materials_tab') as materials_tab:
                materials_tab.disabled = True
                with Container(classes="app-grid"): #Overall container. allows for agile widget placements. 
                    #Here, it uses the 'grid' format spanning 3 columns and 1 row.
                    with VerticalScroll(classes="features"): #left side vertical column, containing the feature fields.

                        #Printer settings
                        yield Static("[b]Materials override", classes="label", id='static_materials_override')

                        yield Horizontal(
                            Static("Material", classes="feature-text", id='static_material'),

                            #Input widgets define an input field.
                            #its "type" attribute allows for active input restriction (either "text", "number", or "integer")
                            #its value is stored in a "value" attribute, 
                            #only accessible through private method "__getattribute__('value')" or publicly through event controls (down below)
                            Select(prompt="Filament material", id="material", options=[('PLA', 'PLA'), ('ABS', 'ABS'), ('PETG', 'PETG')], allow_blank=False),
                            classes="horizontal-layout")

                        yield Static("[b]Extruder changes", classes="label", id='static_extruder_changes')
                        yield Horizontal(
                            Static("Nozzle Diameter (mm)", classes="feature-text", id='static_nozzle_diameter_mm_0_pm'), 
                            Select(value=0.4,prompt="Nozzle diameter (mm)", id="nozzle_diameter_mm_0_pm", 
                                options=[('0.25', 0.25),('0.4', 0.4), ('0.6', 0.6)], allow_blank=False),
                            classes="horizontal-layout")
                            
                        yield Horizontal(
                            Static(f"Filament diameter", classes="feature-text", id='static_filament_diameter_mm_0_pm'),
                            Select(prompt="filament diameter (mm)", id="filament_diameter_mm_0_pm", 
                                options=[('1.75', 1.75),('3.0', 3.0)], allow_blank=False),
                            classes="horizontal-layout")
                    
                        fil_adv_fact =  Horizontal(
                            Static("Filament Linear Advance Factor", classes="feature-text", 
                                id='static_filament_linear_adv_factor_pm'), 
                            Input(value = '0.06',placeholder="filament linear advance factor", 
                                id="filament_linear_adv_factor_pm", type="number", max_length=2, valid_empty=False),
                            classes="horizontal-layout", id='horizontal_filament_linear_adv_factor_pm')

                        yield fil_adv_fact

                        #Other parameters. loops through quality_features to create remaining input fields.
                        for category in materials_features: #category is a key
                            tmp_key_words = [word for word in category.split('_')] #List of words in the feature's name. 
                            #Used solely for proper text display purposes
                            placeholder_value = '' #tmp variable used to concatenate the new title altogether.
                            for word in tmp_key_words:
                                placeholder_value += word + ' '
                            title_tmp = Static(f"[b]{placeholder_value.title()}", classes="label", id=f'static_{category}_pm') #.title() built-in 
                            #function uppercases each starting letter.
                            yield title_tmp
                                                        
                            #Loops through each feature in a category
                            for feature in materials_features[category]:#feature is also a key.
                                tmp_feature_words = [word for word in feature.split('_')]
                                placeholder_value = ''
                                for word in tmp_feature_words:
                                    if word in ['mm', 'c'] and feature.endswith(word):#temporary solution to decorate units. 
                                        #Will find better later.
                                        placeholder_value += f'({word})'
                                    else:     
                                        placeholder_value += word + ' '
                                if not isinstance(materials_features[category][feature], bool):#non bool- features will yield an Input widget,
                                    #while bools will yield a Switch
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}_pm')
                                    feature_input_field = Input(value=f'{materials_features[category][feature]}', placeholder=f"{placeholder_value}", 
                                                                id=f"{feature}_pm", type="number", max_length=5, valid_empty=False)
                                    if feature in start_as_disabled:
                                        feature_input_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                                        feature_text,
                                                        feature_input_field,
                                                        classes="horizontal-layout", 
                                                        id=f"horizontal_{feature}_pm")
                                    # if feature in advanced_features: #features judged too advanced for a beginner 
                                    #     #are by default hidden
                                        # feature_horizontal.display = False
                                    yield feature_horizontal

                                else: #bool features'case
                                    feature_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{feature}_pm')
                                    feature_switch_field = Switch(value=materials_features[category][feature], id =f"{feature}_pm")
                                    if feature in start_as_disabled:
                                        feature_switch_field.disabled = True
                                    feature_horizontal = Horizontal(    
                                        feature_text,
                                        feature_switch_field,
                                        classes="horizontal-layout", id=f"horizontal_{feature}_pm")
                                    # if feature in advanced_features:
                                    #     feature_horizontal.display = False
                                    yield feature_horizontal

                        #Create button. Handled solely by its decorated function down below.
                        yield Button("[b]Create", id="send-pm", disabled=False)
                    
                    
                    with VerticalScroll(classes="event-text"):
                        '''Right column. 
                        Used for active debug purposes by showing the Lua output or eventual warnings.'''
                        yield Static(self.featurecode, id='main-text-pm', classes='text')

            with TabPane("G-code translation", id='printer_lua_tab') as printer_lua_tab:
                printer_lua_tab.disabled = False
                              
                with Container(classes='app-grid-2'):
                    with VerticalScroll(classes='features'):
                        for variable in main_variables:
                            if variable != 'path_type':
                                tmp_variable_words = [word for word in variable.split('_')]
                                placeholder_value = ''
                                for word in tmp_variable_words:
                                    placeholder_value += word + ' '
                                if not isinstance(main_variables[variable], bool):#non bool- variables will yield an Input widget,
                                    #while bools will yield a Switch
                                    variable_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{variable}')
                                    variable_input_field = Input(value=f'{main_variables[variable]}', placeholder=f"{placeholder_value}", 
                                                                id=f"{variable}", type="number", max_length=5, valid_empty=False)
                                    variable_horizontal = Horizontal(    
                                                        variable_text,
                                                        variable_input_field,
                                                        classes="horizontal-layout", 
                                                        id=f"horizontal_{variable}")
                                    # if feature in advanced_features: #features judged too advanced for a beginner 
                                    #     #are by default hidden
                                        # feature_horizontal.display = False
                                    yield variable_horizontal
                                else: #bool features'case
                                    variable_text = Static(f"{placeholder_value}", classes="feature-text", id=f'static_{variable}')
                                    variable_switch_field = Switch(value=main_variables[variable], id =f"{variable}")
                                    variable_horizontal = Horizontal(    
                                        variable_text,
                                        variable_switch_field,
                                        classes="horizontal-layout", id=f"horizontal_{variable}")
                                    # if feature in advanced_features:
                                    #     feature_horizontal.display = False
                                    yield variable_horizontal
                        
                        yield Button("[b]Create", id="send-printer", disabled=True)
                        # variable_static = Static(f"Variable setup", classes="label", id=f'static_variable')
                        # variable_area = TextArea.code_editor(text=f'{main_variables}', classes='features', language='python') 

                        # yield variable_static
                        # yield variable_area
                    with VerticalScroll(classes='event-text-2'):
                        header_static = Static(f"Header", classes="label", id=f'static_header')
                        footer_static = Static(f"Footer", classes="label", id=f'static_footer')
                        header_area = TextArea.code_editor(self.printerheader, classes='features', language='python', id='header')
                        footer_area = TextArea.code_editor(text=self.printerfooter, classes='features', language='python', id='footer')
                        
                        # Register the lua language and highlight query
                        # text_area.register_language(lua_language, lua_highlight_query)
                        # text_area.language = "lua"
                        yield header_static
                        yield header_area

                        yield footer_static
                        yield footer_area

            
    @on(Switch.Changed) #decorator called upon receiving a change in one of the yielded Switch widgets.
    #this decorator declares the following method as a message handler.
    def on_switch_changed(self, event:Switch.Changed) -> None: #the event class gets the switch's id, value, and more.
        if event.switch.id == 'add_brim': #since "add_brim" is a Switch, its "value" attribute can only be a bool
            if event.switch.value == False: #if "add brim" is disabled, dependant features will be disabled and 
                #output as comments in the lua file (see output handler below).

                self.query('#brim_distance_to_print_mm').first().disabled = True#the query('#widget_id') method summons a widget 
                #thanks to its id, giving us access to its methods and attributes.
                self.query('#brim_num_contours').first().disabled = True

            else: #otherwise, toggle them back on and output their values correctly in the lua file.
                self.query('#brim_distance_to_print_mm').first().disabled = False
                self.query('#brim_num_contours').first().disabled = False
            
        if event.switch.id == 'enable_z_lift':#ditto
            if event.switch.value == False:
                self.query('#extruder_swap_zlift_mm').first().disabled = True
                self.query('#z_lift_mm').first().disabled = True
            else:
                self.query('#z_lift_mm').first().disabled = False
                self.query('#z_lift_mm').first().disabled = False

        if event.switch.id == 'enable_acceleration':#displays/hides acceleration-related features in advanced mode,
            #and most importantly, entirely disables/enables its handling.
            self.enableacceleration = event.value
            self.refresh_header(event.value, self.autobedleveling, self.reloadbedmesh)
            self.refresh_footer(event.value)
            
            if event.switch.value == False:
                for feature in accel_features:
                    self.query(f'#{feature}').first().disabled = True
                    self.query(f'#horizontal_{feature}').first().display = False
            else:
                for feature in accel_features:
                    if feature not in ['default_jerk', 'infill_jerk']:
                        self.query(f'#{feature}').first().disabled = False
                    self.query(f'#horizontal_{feature}').first().display = True

        if event.switch.id =='auto_bed_leveling':
            self.autobedleveling = event.value
            self.refresh_header(self.enableacceleration,event.value, self.reloadbedmesh)
        
        if event.switch.id =='reload_bed_mesh':
            self.reloadbedmesh = event.value
            self.refresh_header(self.enableacceleration,event.value, self.reloadbedmesh)

        if event.switch.id == 'advanced_mode':#toggles advanced mode and displays hidden feature fields.
            if event.switch.value == False:
                self.query(f'#horizontal_enable_acceleration').first().display = False
                for feature in advanced_features:
                    self.query(f'#horizontal_{feature}').first().display = False
            else:
                self.query(f'#horizontal_enable_acceleration').first().display = True                
                for feature in advanced_features:
                    self.query(f'#horizontal_{feature}').first().display = True
        
        if event.switch.id == 'heated_chamber':
            self.heatedchamber = event.value
            if event.value:
                self.query('#chamber_temp_degree_c').first().disabled = False
                self.query('#chamber_temp_degree_c_min').first().disabled = False
                self.query('#chamber_temp_degree_c_max').first().disabled = False
                self.query('#chamber_temp_degree_c_pm').first().disabled = False
            else:
                self.query('#chamber_temp_degree_c').first().disabled = True
                self.query('#chamber_temp_degree_c_min').first().disabled = True
                self.query('#chamber_temp_degree_c_max').first().disabled = True
                self.query('#chamber_temp_degree_c_pm').first().disabled = True
        
        if event.switch.id == 'enable_fan_pm':
            if event.value:
                self.query('#fan_speed_percent_pm').first().disabled = False
                self.query('#fan_speed_percent_on_bridges_pm').first().disabled = False
            else:
                self.query('#fan_speed_percent_pm').first().disabled = True
                self.query('#fan_speed_percent_on_bridges_pm').first().disabled = True
        
        if event.switch.id == 'classic_jerk':
            self.classicjerk = event.value
            if event.value:
                self.query('#default_jerk').first().disabled = False
                self.query('#infill_jerk').first().disabled = False

                self.query('#default_junction_deviation').first().disabled = True
                self.query('#perimeter_junction_deviation').first().disabled = True
                self.query('#infill_junction_deviation').first().disabled = True
                self.query('#travel_junction_deviation').first().disabled = True
            else:
                self.query('#default_jerk').first().disabled = True
                self.query('#infill_jerk').first().disabled = True

                self.query('#default_junction_deviation').first().disabled = False
                self.query('#perimeter_junction_deviation').first().disabled =False
                self.query('#infill_junction_deviation').first().disabled = False
                self.query('#travel_junction_deviation').first().disabled = False

    @on(Select.Changed)#handles the case of Select widgets being modified.
    def on_select_changed(self, event:Select.Changed) -> None:
        
        if event.select.id == 'extruder_count':#loops through all hidden features describing additional extruders to display/hide them. 
            #hidden extruder settings will not be written in the lua output at all, for clarity purposes.
            for extruder in range(1, event.select.value): #displays the correct amount of extruders
                self.query(f'#horizontal_nozzle_{extruder}').first().display = True
                self.query(f'#horizontal_fildiam_{extruder}').first().display = True

            for extruder in range (event.select.value, 14):#hides the rest
                self.query(f'#horizontal_nozzle_{extruder}').first().display = False
                self.query(f'#horizontal_fildiam_{extruder}').first().display = False

            self.extrudercount = event.select.value # we store the number of extruders in a reactive variable 
            #as it will be used for the final output.
            if event.value > 1:
                self.query('#extruder_swap_zlift_mm').first().disabled = False
                self.query('#extruder_swap_retract_length_mm').first().disabled = False
                self.query('#extruder_swap_retract_speed_mm_per_sec').first().disabled = False
            else:
                self.query('#extruder_swap_zlift_mm').first().disabled = True
                self.query('#extruder_swap_retract_length_mm').first().disabled = True
                self.query('#extruder_swap_retract_speed_mm_per_sec').first().disabled = True
        if event.select.id == 'bed_circular': # handles the bed shape. 
            #A circular bed (value= True) enables the display of "bed_radius" and deactivates the ability to modify x and y bd sizes 
            #as they are defined as 2* the bed_radius
            if event.select.value == False:
                self.query('#bed_radius').first().disabled = True
                self.query('#horizontal_bed_radius').first().display = False

                self.query('#bed_size_x_mm').first().disabled = False
                self.query('#bed_size_y_mm').first().disabled = False
            else:
                self.query('#bed_radius').first().disabled = False
                self.query('#horizontal_bed_radius').first().display = True

                new_radius = float(self.query('#bed_radius').first().__getattribute__('value'))
                self.query('#bed_size_x_mm').first().__setattr__('value', f'{new_radius*2}')
                self.query('#bed_size_y_mm').first().__setattr__('value', f'{new_radius*2}')

                self.query('#bed_size_x_mm').first().disabled = True
                self.query('#bed_size_y_mm').first().disabled = True
                
        if event.select.id in [f'nozzle_diameter_mm_{i}' for i in range(self.extrudercount)] : #minimum and maximum layer thicknesses 
            #are rescaled values of the nozzle_diameter.
            values = [self.query(f'#nozzle_diameter_mm_{i}').first().__getattribute__('value') for i in range(self.extrudercount)]
            min_nozzle_diam = min(values)
            max_nozzle_diam = max(values)
            self.query('#z_layer_height_mm_min').first().__setattr__('value', f'{round(min_nozzle_diam*0.1, 2)}')
            self.query('#z_layer_height_mm_max').first().__setattr__('value',f'{round(max_nozzle_diam*0.9, 2)}')

        if event.select.id == "firmware":
            self.firmware = event.value
            if event.value != 0: #0 is Marlin; only Marlin supports classic Jerk, and Klipper uses SCV
                self.query('#classic_jerk').first().disabled = True
                self.query('#default_jerk').first().disabled = True
                self.query('#infill_jerk').first().disabled = True
            else:
                self.query('#classic_jerk').first().__setattr__('value', False)
                self.query('#classic_jerk').first().disabled = False




        #default quality values
        if event.select.id == 'quality':
            self.quality = event.value
            if event.value == 'low':
                self.query('#z_layer_height_mm_pq').first().__setattr__('value', str(0.2))
                self.query('#priming_mm_per_sec_pq').first().__setattr__('value', str(30))
                self.query('#print_speed_mm_per_sec_pq').first().__setattr__('value', str(60))
                self.query('#cover_print_speed_mm_per_sec_pq').first().__setattr__('value', str(35))

            if event.value == 'medium':
                self.query('#z_layer_height_mm_pq').first().__setattr__('value', str(0.15))
                self.query('#priming_mm_per_sec_pq').first().__setattr__('value', str(40))
                self.query('#print_speed_mm_per_sec_pq').first().__setattr__('value', str(40))
                self.query('#cover_print_speed_mm_per_sec_pq').first().__setattr__('value', str(25))

            if event.value == 'high':
                self.query('#z_layer_height_mm_pq').first().__setattr__('value', str(0.1))
                self.query('#priming_mm_per_sec_pq').first().__setattr__('value', str(50))
                self.query('#print_speed_mm_per_sec_pq').first().__setattr__('value', str(50))
                self.query('#cover_print_speed_mm_per_sec_pq').first().__setattr__('value', str(30))

        

        if event.select.id == 'material':
            self.material = event.value
            if event.value == 'PLA':
                self.query('#nozzle_diameter_mm_0_pm').first().__setattr__('value', 0.4)
                self.query('#filament_diameter_mm_0_pm').first().__setattr__('value', 1.75)
                self.query('#filament_linear_adv_factor_pm').first().__setattr__('value', str(0.06))
                self.query('#filament_priming_mm_pm').first().__setattr__('value', str(45))
                self.query('#extruder_temp_degree_c_pm').first().__setattr__('value', str(210))
                self.query('#bed_temp_degree_c_pm').first().__setattr__('value', str(60))
                self.query('#fan_speed_percent_pm').first().__setattr__('value', str(100))
                self.query('#fan_speed_percent_on_bridges_pm').first().__setattr__('value', str(100))
                self.query('#print_speed_mm_per_sec_pm').first().__setattr__('value', str(60))
                self.query('#perimeter_print_speed_mm_per_sec_pm').first().__setattr__('value', str(45))
                self.query('#cover_print_speed_mm_per_sec_pm').first().__setattr__('value', str(30))
                self.query('#first_layer_print_speed_mm_per_sec_pm').first().__setattr__('value', str(20))


            if event.value == 'ABS':
                self.query('#nozzle_diameter_mm_0_pm').first().__setattr__('value', 0.6)
                self.query('#filament_diameter_mm_0_pm').first().__setattr__('value', 1.75)
                self.query('#filament_linear_adv_factor_pm').first().__setattr__('value',str(0.04))
                self.query('#filament_priming_mm_pm').first().__setattr__('value', str(45))
                self.query('#extruder_temp_degree_c_pm').first().__setattr__('value', str(240))
                self.query('#bed_temp_degree_c_pm').first().__setattr__('value', str(100))
                self.query('#enable_fan_pm').first().__setattr__('value', False)
                self.query('#fan_speed_percent_pm').first().__setattr__('value', str(100))
                self.query('#fan_speed_percent_on_bridges_pm').first().__setattr__('value', str(100))
                self.query('#print_speed_mm_per_sec_pm').first().__setattr__('value', str(50))
                self.query('#perimeter_print_speed_mm_per_sec_pm').first().__setattr__('value', str(45))
                self.query('#cover_print_speed_mm_per_sec_pm').first().__setattr__('value', str(45))
                self.query('#first_layer_print_speed_mm_per_sec_pm').first().__setattr__('value', str(20))

            if event.value == 'PETG':
                self.query('#nozzle_diameter_mm_0_pm').first().__setattr__('value', 0.6)
                self.query('#filament_diameter_mm_0_pm').first().__setattr__('value', 1.75)
                self.query('#filament_linear_adv_factor_pm').first().__setattr__('value', str(0.08))
                self.query('#extruder_temp_degree_c_pm').first().__setattr__('value', str(230))
                self.query('#bed_temp_degree_c_pm').first().__setattr__('value', str(75))
                self.query('#enable_fan_pm').first().__setattr__('value', True)
                self.query('#fan_speed_percent_pm').first().__setattr__('value', str(45))
                self.query('#fan_speed_percent_on_bridges_pm').first().__setattr__('value', str(75))
                self.query('#print_speed_mm_per_sec').first().__setattr__('value', str(120))
                self.query('#perimeter_print_speed_mm_per_sec_pm').first().__setattr__('value', str(80))
                self.query('#cover_print_speed_mm_per_sec_pm').first().__setattr__('value', str(80))
                self.query('#first_layer_print_speed_mm_per_sec_pm').first().__setattr__('value', str(30))

            
                
    @on(Input.Changed)#handles the case of input widgets being modified.
    def on_input_changed(self, event:Input.Changed) -> None:
        if event.input.id == 'printer_name':
            self.printername = event.value

            if event.validation_result.is_valid == False:
                #error log
                self.featurecode = ''
                for error in event.validation_result.failure_descriptions:
                    self.featurecode += error + '\n'
                self.featurecode += '\nName needed to activate other tabs.'
                self.query_one('#main-text').update(self.featurecode)

                #disables the other tabs
                self.query('#quality_tab').first().disabled = True
                self.query('#materials_tab').first().disabled = True
                self.query('#send').first().disabled = True
                self.query('#send-printer').first().disabled = True
            else:
                self.featurecode = ''
                self.query_one('#main-text').update(self.featurecode)
                self.query_one('#main-text-pq').update(self.featurecode )
                self.query_one('#main-text-pm').update(self.featurecode )

                self.query('#quality_tab').first().disabled = False
                self.query('#materials_tab').first().disabled = False
                self.query('#send').first().disabled = False
                self.query('#send-printer').first().disabled = False



        if event.input.id == 'bed_radius':#auto rescaling of the bed size values.
            if event.value != "":
                self.query('#bed_size_x_mm').first().__setattr__('value', f'{float(event.value)*2}')
                self.query('#bed_size_y_mm').first().__setattr__('value', f'{float(event.value)*2}')

        if event.input.id == 'print_speed_mm_per_sec':
            if event.value != "":
                self.query('#print_speed_mm_per_sec_min').first().__setattr__('value', f'{round(float(event.value)/3, 2)}')
                self.query('#print_speed_mm_per_sec_max').first().__setattr__('value', f'{round(float(event.value)*3.5, 2)}')

                self.query('#perimeter_print_speed_mm_per_sec').first().__setattr__('value', f'{round(float(event.value)*0.75, 2)}')
                self.query('#perimeter_print_speed_mm_per_sec_min').first().__setattr__('value', f'{round(float(event.value)/3, 2)}')
                self.query('#perimeter_print_speed_mm_per_sec_max').first().__setattr__('value', f'{round(float(event.value)*2.8, 2)}')

                self.query('#cover_print_speed_mm_per_sec').first().__setattr__('value', f'{round(float(event.value)*0.75, 2)}')
                self.query('#cover_print_speed_mm_per_sec_min').first().__setattr__('value', f'{round(float(event.value)/3, 2)}')
                self.query('#cover_print_speed_mm_per_sec_max').first().__setattr__('value', f'{round(float(event.value)*2.8, 2)}')

                self.query('#first_layer_print_speed_mm_per_sec').first().__setattr__('value', f'{round(float(event.value)/3, 2)}')
                self.query('#first_layer_print_speed_mm_per_sec_max').first().__setattr__('value', f'{round(float(event.value)*2.8, 2)}')

                self.query('#travel_speed_mm_per_sec').first().__setattr__('value', f'{round(float(event.value)*3, 2)}')
                
        if event.input.id == 'default_acc':
            if event.value != "":
                self.query('#e_prime_max_acc').first().__setattr__('value', f'{round(float(event.value)/2)}')
                self.query('#perimeter_acc').first().__setattr__('value', f'{round(float(event.value)/2)}')
                self.query('#infill_acc').first().__setattr__('value', f'{round(float(event.value))}')
                self.query('#x_max_acc').first().__setattr__('value', f'{round(float(event.value))}')
                self.query('#y_max_acc').first().__setattr__('value', f'{round(float(event.value))}')
                self.query('#z_max_acc').first().__setattr__('value', f'{round(float(event.value)/40)}')
                self.query('#e_max_acc').first().__setattr__('value', f'{round(float(event.value))}')
        
        if event.input.id == 'default_jerk':
            if event.value != "":
                self.query('#infill_jerk').first().__setattr__('value', event.value)

                default_accel = float(self.query('#default_acc').first().__getattribute__('value'))
                perim_accel =  float(self.query('#perimeter_acc').first().__getattribute__('value'))
                infill_accel =  float(self.query('#infill_acc').first().__getattribute__('value')) 
                self.query('#default_junction_deviation').first().__setattr__('value', str(round(0.4*(float(event.value)**2/default_accel), 4)))
                self.query('#perimeter_junction_deviation').first().__setattr__('value', str(round(0.4*(float(event.value)**2/perim_accel), 4)))
                self.query('#infill_junction_deviation').first().__setattr__('value', str(round(0.4*(float(event.value)**2/infill_accel), 4)))
                self.query('#travel_junction_deviation').first().__setattr__('value', str(round(0.4*(float(event.value)**2/default_accel),4)))



###Output handler

    @on(Button.Pressed)#handles the case of the "create" button being pressed.
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'send':
            errorsend = ''
            self.featurecode = "" #empties the output.
            try: #a try and catch section to raise errors when faulty lua outputs are made, i.e. empty values
                if self.printername == '':
                    errorsend = 'Missing value.'
                    raise "Missing Value"
                self.featurecode += '--Custom profile for ' + self.printername +'\n'
                self.featurecode += '--Created on ' +  datetime.now().strftime("%x") +'\n \n'
                self.featurecode += '--Firmware: 0 = Marlin; 1 = RRF; 2 = Klipper; 3 = Others\n'
                self.featurecode += 'firmware = '+ f'{self.query("#firmware").first().__getattribute__("value")}'

                for category in default_features:
                    errorsend = 'category.'
                    self.featurecode += '\n \n'+ f'--{category}' # puts said category as a commented title. solely for clarity purposes.
                    for feature in default_features[category]:
                        errorsend = 'feature.'
                        feature_value = str(self.query(f'#{feature}').first().__getattribute__('value')) #use of the private "__getattribute__" 
                        #method to query the field's value.
                        errorsend = 'query_value.'
                        if self.query(f'#{feature}').first().disabled == False or feature in ['bed_size_x_mm', 'bed_size_y_mm']: 
                            #only enabled features are output normally, except for bed sizes as they are only deactivated 
                            #in case of a circular bed.
                            if feature_value == '': # avoids empty fields.
                                errorsend = 'missing value 2.'
                                raise "Missing Value"
                            else:#due to laziness, every feature_value is lowercased so that specifically bool values get lowercased, 
                                #thanks to lua's odd syntax.
                                errorsend = 'lowercased.' 
                                self.featurecode += '\n'+ f'{feature} = ' + feature_value.lower()
                                self.query('#main-text').first().update(f'{self.featurecode}')
                                errorsend = 'query update 1.'
                        else:#disabled features are output as lua comments.
                            errorsend = 'disabled.'
                            self.featurecode += '\n'+ f'--{feature} = ' + feature_value.lower()
                            self.query('#main-text').first().update(f'{self.featurecode}')
                            errorsend = 'query update 2.'

                for extruder in range(1, int(self.extrudercount)): #handles similar actions for every additonal extruder settings. 
                    #If no additional extruder, no additional comments shall be written.
                    errorsend = 'extruders.'
                    nozzle_value = str(self.query(f'#nozzle_diameter_mm_{extruder}').first().__getattribute__('value'))
                    errorsend = 'extruders query 1.'
                    self.featurecode += '\n'+ f'nozzle_diameter_mm_{extruder} = ' + nozzle_value
                    fildiam_value = str(self.query(f'#filament_diameter_mm_{extruder}').first().__getattribute__('value'))
                    errorsend = 'extruders query 2.'
                    self.featurecode += '\n'+ f'filament_diameter_mm_{extruder} = ' + fildiam_value
                    self.query('#main-text').first().update(f'{self.featurecode}')
                    errorsend = 'extruders query 3.'

                for category in features_dict:#handles similar action for remaining features.
                    errorsend = 'category 2.'
                    self.featurecode += '\n \n'+ f'--{category}'
                    for feature in features_dict[category]:
                        errorsend = 'features 2.'
                        feature_value = str(self.query(f'#{feature}').first().__getattribute__('value'))
                        errorsend = 'query value 2.'
                        if self.query(f'#{feature}').first().disabled == False:
                            if feature_value == '':
                                errorsend = 'missing value 2.'
                                raise "Missing Value"
                            else:
                                errorsend = 'lowercased 2.'
                                self.featurecode += '\n'+ f'{feature} = ' + feature_value.lower()
                                self.query('#main-text').first().update(f'{self.featurecode}')
                                errorsend = 'query update 3.'
                        else:
                            errorsend = 'disabled 2.'
                            self.featurecode += '\n'+ f'--{feature} = ' + feature_value.lower()
                            self.query('#main-text').first().update(f'{self.featurecode}')
                            errorsend = 'query update 4.'

                ## Folder creation (if it does not exist yet) and lua file dumping.
                printer_name_words = self.printername.split(' ')
                printer_name = ''
                for word in printer_name_words:
                    if word != printer_name_words[-1]:
                        printer_name += word + '_'
                    else:
                        printer_name += word
                
                if f"{printer_name}" not in os.listdir():
                    os.makedirs(f'{printer_name}')
                dump_file = open(f'./{printer_name}/features.lua', 'w')
                dump_file.write(self.featurecode)
                self.copy_to_clipboard(self.featurecode)
                self.query('#printer_lua_tab').first().disabled = False
            except:#if not successful, displays the following in the right panel.
                self.featurecode = errorsend + "\nPlease fill any empty information field(s)."
                self.query('#main-text').first().update(f'{self.featurecode}')



        #QUALITY PROFILE
        if event.button.id == 'send-pq':
            errorsend = ''
            self.featurecode = "" #empties the output.
            try: #a try and catch section to raise errors when faulty lua outputs are made, i.e. empty values
                if self.quality == '':
                    errorsend = 'Missing value.'
                    raise "Missing Value"
                self.featurecode += '--Custom quality profile: ' + self.quality + f' for {self.printername} \n'
                self.featurecode += '--Created on ' +  datetime.now().strftime("%x") +'\n \n'

                for category in quality_features:
                    errorsend = 'category.'
                    self.featurecode += '\n \n'+ f'--{category}' # puts said category as a commented title. solely for clarity purposes.
                    for feature in quality_features[category]:
                        errorsend = 'feature.'
                        feature_value = str(self.query(f'#{feature}_pq').first().__getattribute__('value')) #use of the private "__getattribute__" 
                        #method to query the field's value.
                        errorsend = 'query_value.'
                        if self.query(f'#{feature}_pq').first().disabled == False: 
                            #only enabled features are output normally, except for bed sizes as they are only deactivated 
                            #in case of a circular bed.
                            if feature_value == '': # avoids empty fields.
                                errorsend = 'missing value 2.'
                                raise "Missing Value"
                            else:#due to laziness, every feature_value is lowercased so that specifically bool values get lowercased, 
                                #thanks to lua's odd syntax.
                                errorsend = 'lowercased.' 
                                self.featurecode += '\n'+ f'{feature} = ' + feature_value.lower()
                                self.query('#main-text-pq').first().update(f'{self.featurecode}')
                                errorsend = 'query update 1.'
                        else:#disabled features are output as lua comments.
                            errorsend = 'disabled.'
                            self.featurecode += '\n'+ f'--{feature} = ' + feature_value.lower()
                            self.query('#main-text-pq').first().update(f'{self.featurecode}')
                            errorsend = 'query update 2.'


                ## Folder creation (if it does not exist yet) and lua file dumping.
                quality_name_words = self.quality.split(' ')
                quality_name = ''
                for word in quality_name_words:
                    if word != quality_name_words[-1]:
                        quality_name += word + '_'
                    else:
                        quality_name += word
                
                if f"{self.printername}" not in os.listdir():
                    os.makedirs(f'{self.printername}/profiles')
                dump_file = open(f'./{self.printername}/profiles/{self.quality}.lua', 'w')
                dump_file.write(self.featurecode)
                self.copy_to_clipboard(self.featurecode)
                
            except:#if not successful, displays the following in the right panel.
                self.featurecode = errorsend + "\nPlease fill any empty information field(s)."
                self.query('#main-text-pq').first().update(f'{self.featurecode}')    


        #MATERIAL PROFILE
        if event.button.id == 'send-pm':
            errorsend = ''
            self.featurecode = "" #empties the output.
            try: #a try and catch section to raise errors when faulty lua outputs are made, i.e. empty values
                if self.quality == '':
                    errorsend = 'Missing value.'
                    raise "Missing Value"
                self.featurecode += '--Custom material profile: ' + self.material + f' for {self.printername} \n'
                self.featurecode += '--Created on ' +  datetime.now().strftime("%x") +'\n \n'

                self.featurecode += '\n \n'+ '--extruder_changes'
                errorsend = 'nu'
                self.featurecode += '\n'+ 'nozzle_diameter_mm_0 = ' + f'{self.query("#nozzle_diameter_mm_0_pm").first().__getattribute__("value")}'
                errorsend = 'nus'
                self.featurecode += '\n'+ 'filament_diameter_mm_0 = ' + f'{self.query("#filament_diameter_mm_0_pm").first().__getattribute__("value")}'
                errorsend = 'nuq'
                self.featurecode += '\n'+ 'filament_linear_adv_factor = ' + str(self.query("#filament_linear_adv_factor_pm").first().__getattribute__("value"))

                for category in materials_features:
                    errorsend = 'category.'
                    self.featurecode += '\n \n'+ f'--{category}' # puts said category as a commented title. solely for clarity purposes.
                    for feature in materials_features[category]:
                        errorsend = 'feature.'
                        feature_value = str(self.query(f'#{feature}_pm').first().__getattribute__('value')) #use of the private "__getattribute__" 
                        #method to query the field's value.
                        errorsend = 'query_value.'
                        if self.query(f'#{feature}_pm').first().disabled == False: 
                            #only enabled features are output normally, except for bed sizes as they are only deactivated 
                            #in case of a circular bed.
                            if feature_value == '': # avoids empty fields.
                                errorsend = 'missing value 2.'
                                raise "Missing Value"
                            else:#due to laziness, every feature_value is lowercased so that specifically bool values get lowercased, 
                                #thanks to lua's odd syntax.
                                errorsend = 'lowercased.' 
                                self.featurecode += '\n'+ f'{feature} = ' + feature_value.lower()
                                self.query('#main-text-pm').first().update(f'{self.featurecode}')
                                errorsend = 'query update 1.'
                        else:#disabled features are output as lua comments.
                            errorsend = 'disabled.'
                            self.featurecode += '\n'+ f'--{feature} = ' + feature_value.lower()
                            self.query('#main-text-pm').first().update(f'{self.featurecode}')
                            errorsend = 'query update 2.'


                ## Folder creation (if it does not exist yet) and lua file dumping.
                material_name_words = self.material.split(' ')
                material_name = ''
                for word in material_name_words:
                    if word != material_name_words[-1]:
                        material_name += word + '_'
                    else:
                        material_name += word
                
                if f"{self.printername}" not in os.listdir():
                    os.makedirs(f'{self.printername}/materials')
                dump_file = open(f'./{self.printername}/materials/{self.material}.lua', 'w')
                dump_file.write(self.featurecode)
                self.copy_to_clipboard(self.featurecode)
                
            except:#if not successful, displays the following in the right panel.
                self.featurecode = errorsend + "\nPlease fill any empty information field(s)."
                self.query('#main-text-pm').first().update(f'{self.featurecode}')


        if event.button.id == 'send-printer':
            errorsend = ''
            self.printercode = ''
            try:
                errorsend = 'start'
                self.printercode += '--Printer functions for' + self.printername +'\n'
                self.printercode += '--Created on ' +  datetime.now().strftime("%x") +'\n \n'
                self.printercode += "output(';FLAVOR:Marlin')"
                self.printercode += "output(';Layer height: ' .. round(z_layer_height_mm,2))"
                self.printercode += "output(';Generated with ' .. slicer_name .. ' ' .. slicer_version .. '\n')"
                self.printercode += '--//////////////////////////////////////////////////Defining main variables\n'
                
                for variable in main_variables:
                    errorsend = 'varqqqqqqqq'
                    variable_value = str(self.query(f'#{variable}').first().__getattribute__('value'))  #use of the private "__getattribute__"
                    errorsend = 'qweqwr'
                    self.printercode += '\n'+ f'{variable} = ' + variable_value.lower()
                    errorsend = 'qwr'
                
                self.printercode += '''

path_type = {
--{ 'default',    'Craftware'}
  { ';perimeter',  ';segType:Perimeter' },
  { ';shell',      ';segType:HShell' },
  { ';infill',     ';segType:Infill' },
  { ';raft',       ';segType:Raft' },
  { ';brim',       ';segType:Skirt' },
  { ';shield',     ';segType:Pillar' },
  { ';support',    ';segType:Support' },
  { ';tower',      ';segType:Pillar'}
}

'''
                errorsend = 'writing'
                self.printercode += '--//////////////////////////////////////////////////Main Functions - called by IceSL \n'
                self.printercode += '--################################################## HEADER & FOOTER \n'

                self.printercode += self.printerheader
                self.printercode += '-----------------------\n'

                self.printercode += self.printerfooter + '\n'
                self.printercode += '--################################################## COMMENT'

                ## Folder creation (if it does not exist yet) and lua file dumping.
                errorsend = 'dumping'
                printer_name_words = self.printername.split(' ')
                printer_name = ''
                for word in printer_name_words:
                    if word != printer_name_words[-1]:
                        printer_name += word + '_'
                    else:
                        printer_name += word
                    
                    if f"{printer_name}" not in os.listdir():
                        os.makedirs(f'{printer_name}')
                    dump_file = open(f'./{printer_name}/printer.lua', 'w')
                    dump_file.write(self.printercode)
                    self.copy_to_clipboard(self.printercode)
            except: 
                #if not successful, displays the following log in the right panel.
                self.printercode = errorsend + "\nNOPE."
                self.query('#main-text').first().update(f'{self.printercode}')

###lua code refreshers
    def refresh_header(self, accel_Enabled, auto_bed_leveling_Enabled, reload_bed_mesh_Enabled) -> None:
        self.printerheader = '''function header()

    -- called to create the header of the G-Code file.

    output('G21 ; set units to millimeters')
    output('G90 ; use absolute coordinates')
    output('M82 ; extruder absolute mode') --constant
        '''

        if accel_Enabled:
            self.printerheader += '''
    --set limits
    output('M201 X' .. x_max_acc .. ' Y' .. y_max_acc .. ' Z' .. z_max_acc .. ' E' .. e_max_acc .. ' ; sets maximum accelerations, mm/sec^2')
    output('M203 X' .. x_max_speed .. ' Y' .. y_max_speed .. ' Z' .. z_max_speed .. ' E' .. e_max_speed .. ' ; sets maximum feedrates, mm/sec')
    output('M204 P' .. default_acc .. ' R' .. e_prime_max_acc .. ' T' .. default_acc .. ' ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2')
    output('M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec')
    output('M205 J' .. default_junction_deviation .. ' ; sets Junction Deviation')
        '''
        self.printerheader += '''
    output('')

    output('M109 R' .. extruder_temp_degree_c[extruders[0]] .. ' ; set extruder temp')
    output('M190 S' .. bed_temp_degree_c .. ' ; wait for bed temp')
    '''
        if self.heatedchamber:
            self.printerheader += '''
    output('M191 R' .. chamber_temp_degree_c .. ' ; set and wait chamber temperature')
'''
        self.printerheader +='''
    output('M107')
    output('G28 ; home all without mesh bed level')

    '''
        if auto_bed_leveling_Enabled and not reload_bed_mesh_Enabled:
            self.printerheader += '''
    --start auto bed leveling
    output('G29 ; auto bed leveling')
    output('G0 F' .. travel_speed_mm_per_sec * 60 .. 'X0 Y0 ; back to the origin to begin the purge')
    '''
        elif reload_bed_mesh_Enabled:
            self.printerheader +='''
    --start auto bed leveling and reload previous bed mesh
    output('M420 S1 ; enable bed leveling (was disabled y G28)')
    output('M420 L ; load previous bed mesh')
    '''

        self.printerheader += '''
    output('M109 S' .. extruder_temp_degree_c[extruders[0]] .. ' ; wait for extruder temp')

    output('')
    --set Linear Advance k-factor
    output('M900 K' .. filament_linear_adv_factor .. ' ; Linear/Pressure advance')

    current_frate = travel_speed_mm_per_sec * 60
    changed_frate = true

end
'''

        self.query('#header').first().__setattr__('text', self.printerheader)

    def refresh_footer(self, accel_Enabled) -> None:
        self.printerfooter = '''
function footer()
    --called to create the footer of the G-Code file.

    output('')
    output('G4 ; wait')
    output('M104 S0 ; turn off temperature')
    output('M140 S0 ; turn off heatbed')
    '''
        if self.heatedchamber:
            self.printerfooter +='''
    output('M141 S0 ; turn off heated chamber')
'''
        self.printerfooter +='''

    output('M107 ; turn off fan')
    output('G28 X Y ; home X and Y axis')
    output('G91')
    output('G0 Z 10') -- move in Z to clear space between print and nozzle
    output('G90')
    output('M84 ; disable motors')
    output('')
    '''

        if accel_Enabled:
            self.printerfooter += '''
    --set limits back to original values.
    output('M201 X' .. x_max_acc .. ' Y' .. y_max_acc .. ' Z' .. z_max_acc .. ' E' .. e_max_acc .. ' ; sets maximum accelerations, mm/sec^2')
    output('M203 X' .. x_max_speed .. ' Y' .. y_max_speed .. ' Z' .. z_max_speed .. ' E' .. e_max_speed .. ' ; sets maximum feedrates, mm/sec')
    output('M204 P' .. default_acc .. ' R' .. e_prime_max_acc .. ' T' .. default_acc .. ' ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2')
    output('M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec')
    output('M205 J' .. default_junction_deviation .. ' ; sets Junction Deviation')
            '''
        self.printerfooter += '''
end
'''

        self.query('#footer').first().__setattr__('text', self.printerfooter)

    def on_mount(self) -> None:
        '''on mount -> when the app initialises on the terminal.   
        Only used here to define stylistic attributes such as screen background color.'''

        self.screen.styles.background ='#E8E9F3' # type: ignore

        #Tooltips:
        for key in tooltips:
            self.query(f'#{key}').first().tooltip  = tooltips[key]

        self.refresh_header(False, False, False)
        self.refresh_footer(False)

def isNotSpaces(text: str):
    return not(text.strip() == '')

if __name__ == '__main__':
    app = gui()
    app.run()