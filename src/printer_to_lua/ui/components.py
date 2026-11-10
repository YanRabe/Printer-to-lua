"""Reusable presentation components for the Textual application."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from textual.containers import Container, Horizontal, VerticalScroll
from textual.validation import Function, Number
from textual.widgets import Button, Input, Select, Static, Switch, TextArea
from textual.widgets import TabPane

from printer_to_lua.data.features import default_features, features_dict


def is_not_spaces(text: str) -> bool:
    """Return whether a field contains non-whitespace text."""
    return bool(text.strip())


class GeneratedOutput(Static):
    """Display generated Lua content in a named output pane."""

    def set_content(self, content: str) -> None:
        """Replace the displayed generated content."""
        self.update(content)


class FeaturesTab(TabPane):
    """Complete printer feature configuration form."""

    def __init__(self, output: str) -> None:
        super().__init__("Features")
        self._output = output


    def compose(self):
        with Container(
            classes="app-grid"
        ):  # Overall container. allows for agile widget placements.
            # Here, it uses the 'grid' format spanning 3 columns and 1 row.
            with VerticalScroll(
                classes="features"
            ):  # left side vertical column, containing the feature fields.

                # Advanced mode label and button
                yield Horizontal(  # Horizontal widgets are solely used to contain other subwidgets,
                    # and allows to hide/display all of its children at once.
                    Static(
                        "[b]Advanced mode",
                        classes="feature-text",
                        id="static_advanced_mode",
                    ),  # Static widgets define immutable
                    # renderable objects. mainly used for plain texts
                    Switch(
                        value=False, id="advanced_mode", classes='important_toggle', animate=False
                    ),  # Switch widgets define a toggle-switch with value False and True in accordance
                    # to its state.
                    classes="container",
                )  # the "classes" attribute is similar to its Web counterpart, refering the css file.

                # Printer settings
                yield Static("[b]Printer", classes="label", id="static_printer")

                yield Horizontal(
                    Static(
                        "Printer's name",
                        classes="feature-text",
                        id="static_name",
                    ),
                    # Input widgets define an input field.
                    # its "type" attribute allows for active input restriction (either "text", "number", or "integer")
                    # its value is stored in a "value" attribute,
                    # only accessible through private method "__getattribute__('value')" or publicly through event controls (down below)
                    Input(
                        placeholder="Printer's name",
                        id="name",
                        type="text",
                        max_length=104,
                        valid_empty=False,
                        validators=[Function(is_not_spaces, "empty name")],
                    ),
                    classes="horizontal-layout",
                )
                yield Horizontal(
                    Static(
                        "Firmware", classes="feature-text", id="static_firmware"
                    ),
                    # Select widgets define a scrollable field.
                    # its "options" attribute define possible choices through the tuple: ("display name", true_value)
                    # getting the "value" of a Select widget grants the "true_value" variable of the active selection.
                    # It is accessible through private method "__getattribute__('value')" or publicly through event controls.
                    Select(
                        id="firmware",
                        prompt="Firmware",
                        options=[
                            ("Marlin", 0),
                            ("Rep Rap", 1),
                            ("Klipper", 2),
                        ],
                        allow_blank=False,
                    ),
                    classes="horizontal-layout",
                )

                # Build Area Dimensions
                yield Static(
                    "[b]Build Area Dimensions",
                    classes="label",
                    id="static_build_area_dimensions",
                )

                yield Horizontal(
                    Static(
                        "Bed Shape",
                        classes="feature-text",
                        id="static_bed_circular",
                    ),
                    Select(
                        value=False,
                        prompt="bed shape",
                        allow_blank=False,
                        options=[("rectangular", False), ("circular", True)],
                        id="bed_circular",
                    ),
                    classes="container",
                )
                bed_radius_input = Input(
                    value=f'{default_features["build_area_dimensions"]["bed_radius"][0]}',
                    placeholder="bed radius",
                    id="bed_radius",
                    type="number",
                    max_length=10,
                    valid_empty=False,
                    validators=[
                        Function(
                            is_not_spaces, "empty value"
                        ),
                        Number(default_features["build_area_dimensions"]["bed_radius"][2],
                                default_features["build_area_dimensions"]["bed_radius"][3],
                                "Invalid number")
                                ]
                )
                bed_radius_input.disabled = default_features["build_area_dimensions"]["bed_radius"][5]
                bed_radius_widget = Horizontal(
                    Static(
                        "Bed Radius",
                        classes="feature-text",
                        id="static_bed_radius",
                    ),
                    bed_radius_input,
                    classes="horizontal-layout",
                    id="horizontal_bed_radius",
                )
                bed_radius_widget.display = default_features["build_area_dimensions"]["bed_radius"][4]  # Hides the widget.
                yield bed_radius_widget

                yield Horizontal(
                    Static(
                        "Bed Size x (mm)",
                        classes="feature-text",
                        id="static_bed_size_x_mm",
                    ),
                    Input(
                        value=f'{default_features["build_area_dimensions"]["bed_size_x_mm"][0]}',
                        placeholder="bed size x mm ",
                        id="bed_size_x_mm",
                        type="number",
                        max_length=10,
                        valid_empty=False,
                        validators=[
                            Function(
                                is_not_spaces, "empty value"
                            ),
                            Number(default_features["build_area_dimensions"]["bed_size_x_mm"][2],
                                    default_features["build_area_dimensions"]["bed_size_x_mm"][3],
                                    "Invalid number")
                                    ]
                    ),
                    classes="horizontal-layout",
                )
                yield Horizontal(
                    Static(
                        "Bed Size y (mm)",
                        classes="feature-text",
                        id="static_bed_size_y_mm",
                    ),
                    Input(
                        value=f'{default_features["build_area_dimensions"]["bed_size_y_mm"][0]}',
                        placeholder="bed size y mm ",
                        id="bed_size_y_mm",
                        type="number",
                        max_length=10,
                        valid_empty=False,
                        validators=[
                            Function(
                                is_not_spaces, "empty value"
                            ),
                            Number(default_features["build_area_dimensions"]["bed_size_y_mm"][2],
                                    default_features["build_area_dimensions"]["bed_size_y_mm"][3],
                                    "Invalid number")
                                    ]
                    ),
                    classes="horizontal-layout",
                )
                yield Horizontal(
                    Static(
                        "Bed Size z (mm)",
                        classes="feature-text",
                        id="static_bed_size_z_mm",
                    ),
                    Input(
                        value=f'{default_features["build_area_dimensions"]["bed_size_z_mm"][0]}',
                        placeholder="bed size z mm ",
                        id="bed_size_z_mm",
                        type="number",
                        max_length=10,
                        valid_empty=False,
                        validators=[
                            Function(
                                is_not_spaces, "empty value"
                            ),
                            Number(default_features["build_area_dimensions"]["bed_size_z_mm"][2],
                                    default_features["build_area_dimensions"]["bed_size_z_mm"][3],
                                    "Invalid number")
                                    ]
                    ),
                    classes="horizontal-layout",
                )

                # Printer Extruder
                yield Static(
                    "[b]Extruder Settings",
                    classes="label",
                    id="static_extruder_settings",
                )

                yield Horizontal(
                    Static(
                        "Extruder count",
                        classes="feature-text",
                        id="static_extruder_count",
                    ),
                    Select(
                        prompt="extruder count",
                        id="extruder_count",
                        options=[(f"{i}", i) for i in range(1, 15)],
                        allow_blank=False,
                    ),
                    classes="horizontal-layout",
                )

                yield Horizontal(
                    Static(
                        "Nozzle Diameter (mm)",
                        classes="feature-text",
                        id="static_nozzle_diameter_mm_0",
                    ),
                    Select(
                        value=0.4,
                        prompt="Nozzle diameter (mm)",
                        id="nozzle_diameter_mm_0",
                        options=[("0.25", 0.25), ("0.4", 0.4), ("0.6", 0.6)],
                        allow_blank=False,
                    ),
                    classes="horizontal-layout",
                )

                yield Horizontal(
                    Static(
                        f"Filament diameter",
                        classes="feature-text",
                        id="static_filament_diameter_mm_0",
                    ),
                    Select(
                        prompt="filament diameter (mm)",
                        id="filament_diameter_mm_0",
                        options=[("1.75", 1.75), ("2.85", 2.85)],
                        allow_blank=False,
                    ),
                    classes="horizontal-layout",
                )

                # loop to generate doublons of extruder settings, in case there are more than one.
                # maximum number for supported printers is 14 with the Addiform, thus explaining the loop range.
                for i in range(2, 15):
                    title_nozzle = Static(
                        f"Nozzle Diameter for extruder {i} (mm)",
                        classes="feature-text",
                        id=f"static_nozzle_diameter_mm_{i-1}",
                    )
                    input_field_nozzle = Select(
                        value=0.4,
                        prompt=f"Nozzle diameter for extruder {i} (mm)",
                        id=f"nozzle_diameter_mm_{i-1}",
                        options=[("0.25", 0.25), ("0.4", 0.4), ("0.6", 0.6)],
                        allow_blank=False,
                    )
                    horizontal_nozzle = Horizontal(
                        title_nozzle,
                        input_field_nozzle,
                        classes="horizontal-layout",
                        id=f"horizontal_nozzle_{i-1}",
                    )
                    horizontal_nozzle.display = False
                    yield horizontal_nozzle

                    title_fildiam = Static(
                        f"Filament diameter for extruder {i} (mm)",
                        classes="feature-text",
                        id=f"static_filament_diameter_mm_{i-1}",
                    )
                    input_field_fildiam = Select(
                        value=1.75,
                        prompt=f"filament diameter for extruder {i} (mm)",
                        id=f"filament_diameter_mm_{i-1}",
                        options=[("1.75", 1.75), ("3.0", 3.0)],
                        allow_blank=False,
                    )
                    horizontal_fildiam = Horizontal(
                        title_fildiam,
                        input_field_fildiam,
                        classes="horizontal-layout",
                        id=f"horizontal_fildiam_{i-1}",
                    )
                    horizontal_fildiam.display = False
                    yield horizontal_fildiam

                fil_adv_fact = Horizontal(
                    Static(
                        "Filament Linear Advance Factor",
                        classes="feature-text",
                        id="static_filament_linear_adv_factor",
                    ),
                    Input(
                        value=f'{default_features["extruder"]["filament_linear_adv_factor"][0]}',
                        placeholder="filament linear advance factor",
                        id="filament_linear_adv_factor",
                        type="number",
                        max_length=10,
                        valid_empty=False,
                        validators=[
                            Function(
                                is_not_spaces, "empty value"
                            ),
                            Number(default_features["extruder"]["filament_linear_adv_factor"][2],
                                    default_features["extruder"]["filament_linear_adv_factor"][3],
                                    "Invalid number")
                                    ]
                    ),
                    classes="horizontal-layout",
                    id="horizontal_filament_linear_adv_factor",
                )
                fil_adv_fact.display = not default_features["extruder"]["filament_linear_adv_factor"][4]
                yield fil_adv_fact

                # Other parameters. loops through features_dict to create remaining input fields.
                for category in features_dict:  # category is a key
                    tmp_key_words = [
                        word for word in category.split("_")
                    ]  # List of words in the feature's name.
                    # Used solely for proper text display purposes

                    placeholder_value = ""  # tmp variable used to concatenate the new title altogether.
                    for word in tmp_key_words:
                        placeholder_value += word + " "

                    title_tmp = Static(
                        f"[b]{placeholder_value.title()}",
                        classes="label",
                        id=f"static_{category}",
                    )  # .title() built-in function uppercases each starting letter.
                    # acceleration settings is a special case as it is shown only after toggling "enable acceleration" in advanced mode
                    if category != "acceleration_settings":
                        yield title_tmp
                    else:
                        yield title_tmp
                        # the "enable acceleration toggle-switch"
                        enable_accel = Horizontal(
                            Static(
                                "Enable acceleration",
                                classes="feature-text",
                                id="static_enable_acceleration",
                            ),
                            Switch(
                                value=False,
                                id="enable_acceleration",
                                animate=False,
                            ),
                            classes="container",
                            id="horizontal_enable_acceleration",

                        )
                        enable_accel.display = False
                        yield enable_accel

                    # Loops through each feature in a category
                    for feature in features_dict[
                        category
                    ]:  # feature is also a key.
                        tmp_feature_words = [
                            word for word in feature.split("_")
                        ]
                        placeholder_value = ""
                        for word in tmp_feature_words:
                            if word in ["mm", "c"] and feature.endswith(
                                word
                            ):  # temporary solution to decorate units.
                                # Will find better later.
                                placeholder_value += f"({word})"
                            else:
                                placeholder_value += word + " "

                        if features_dict[category][feature][1] != 'bool':  # non bool- features will yield an Input widget,
                            # while bools will yield a Switch
                            feature_text = Static(
                                f"{placeholder_value}",
                                classes="feature-text",
                                id=f"static_{feature}",
                            )
                            feature_input_field = Input(
                                value=f"{features_dict[category][feature][0]}",
                                placeholder=f"{placeholder_value}",
                                id=f"{feature}",
                                type="number",
                                max_length=10,
                                valid_empty=False,
                                validators=[
                                    Function(
                                        is_not_spaces, "empty value"
                                    ),
                                    Number(features_dict[category][feature][2],
                                            features_dict[category][feature][3],
                                            "Invalid number")
                                            ],
                                disabled=features_dict[category][feature][5]
                            )
                            feature_horizontal = Horizontal(
                                feature_text,
                                feature_input_field,
                                classes="horizontal-layout",
                                id=f"horizontal_{feature}",
                            )

                            if features_dict[category][feature][4]:
                                # Advanced features are hidden until advanced mode is enabled.
                                feature_horizontal.display = False
                            yield feature_horizontal

                        else:  # bool features'case
                            feature_text = Static(
                                f"{placeholder_value}",
                                classes="feature-text",
                                id=f"static_{feature}",
                            )
                            feature_switch_field = Switch(
                                value=features_dict[category][feature][0],
                                id=f"{feature}",
                                animate= False,
                                disabled=features_dict[category][feature][5]
                            )
                            feature_horizontal = Horizontal(
                                feature_text,
                                feature_switch_field,
                                classes="horizontal-layout",
                                id=f"horizontal_{feature}",
                            )
                            if features_dict[category][feature][4] == True:
                                feature_horizontal.display = False
                            yield feature_horizontal

                # Create button. Handled solely by its decorated function down below.
                yield Button("[b]Create", id="send", disabled=True)

            with VerticalScroll(classes="event-text"):
                """Right column.
                Used for active debug purposes by showing the Lua output or eventual warnings.
                """
                yield GeneratedOutput(
                    self._output, id="main-text", classes="text"
                )


class ProfileTab(TabPane):
    """Data-driven quality or material profile editor."""

    def __init__(
        self,
        title: str,
        tab_id: str,
        heading: str,
        selection_label: str,
        selection_id: str,
        selection_options: Sequence[tuple[str, str]],
        groups: Mapping[str, Mapping[str, tuple[Any, str, Any, Any, bool, bool]]],
        field_suffix: str,
        button_id: str,
        output_id: str,
        output: str,
        *,
        disabled: bool = True,
    ) -> None:
        super().__init__(title, id=tab_id)
        self._heading = heading
        self._selection_label = selection_label
        self._selection_id = selection_id
        self._selection_options = selection_options
        self._groups = groups
        self._field_suffix = field_suffix
        self._button_id = button_id
        self._output_id = output_id
        self._output = output
        self.disabled = disabled


    @staticmethod
    def _label(value: str) -> str:
        return " ".join(
            f"({word})" if word in {"mm", "c"} and value.endswith(word) else word
            for word in value.split("_")
        )


    def compose(self):
        with Container(classes="app-grid"):
            with VerticalScroll(classes="features"):
                heading_id = (
                    "static_quality_presets"
                    if self._selection_id == "quality"
                    else "static_materials_override"
                )
                selection_static_id = (
                    "static_quality_level"
                    if self._selection_id == "quality"
                    else "static_material"
                )
                yield Static(self._heading, classes="label", id=heading_id)
                yield Horizontal(
                    Static(
                        self._selection_label,
                        classes="feature-text",
                        id=selection_static_id,
                    ),
                    Select(
                        prompt=self._selection_label,
                        id=self._selection_id,
                        options=self._selection_options,
                        allow_blank=False,
                    ),
                    classes="horizontal-layout",
                )
                if self._selection_id == "material":
                    for feature in ("nozzle_diameter_mm_0", "filament_diameter_mm_0"):
                        default, feature_type, minimum, maximum, _, disabled = (
                            default_features["extruder"][feature]
                        )
                        yield Horizontal(
                            Static(self._label(feature), classes="feature-text"),
                            Input(
                                value=f"{default}",
                                placeholder=self._label(feature),
                                id=f"{feature}_pm",
                                type="number",
                                max_length=10,
                                valid_empty=False,
                                validators=[
                                    Function(is_not_spaces, "empty value"),
                                    Number(minimum, maximum, "Invalid number"),
                                ],
                                disabled=disabled,
                            ),
                            classes="horizontal-layout",
                            id=f"horizontal_{feature}_pm",
                        )
                for category, features in self._groups.items():
                    yield Static(
                        f"[b]{self._label(category).title()}",
                        classes="label",
                        id=f"static_{category}_{self._field_suffix}",
                    )
                    for feature, metadata in features.items():
                        default, feature_type, minimum, maximum, _, disabled = metadata
                        label = self._label(feature)
                        if feature_type != "bool":
                            field = Input(
                                value=f"{default}",
                                placeholder=label,
                                id=f"{feature}_{self._field_suffix}",
                                type="number",
                                max_length=10,
                                valid_empty=False,
                                validators=[
                                    Function(is_not_spaces, "empty value"),
                                    Number(minimum, maximum, "Invalid number"),
                                ],
                                disabled=disabled,
                            )
                        else:
                            field = Switch(
                                value=default,
                                id=f"{feature}_{self._field_suffix}",
                                animate=False,
                                disabled=disabled,
                            )
                        yield Horizontal(
                            Static(label, classes="feature-text"),
                            field,
                            classes="horizontal-layout",
                            id=f"horizontal_{feature}_{self._field_suffix}",
                        )
                yield Button("[b]Create", id=self._button_id, disabled=False)
            with VerticalScroll(classes="event-text"):
                yield GeneratedOutput(self._output, id=self._output_id, classes="text")


class PrinterEditorTab(TabPane):
    """Firmware-aware printer variable and Lua editor tab."""

    def __init__(
        self,
        main_variables: Mapping[str, Any],
        function_dict: Mapping[str, Mapping[str, str]],
        header: str,
        footer: str,
        *,
        disabled: bool = False,
    ) -> None:
        super().__init__("G-code translation", id="gcode_tab")
        self._main_variables = main_variables
        self._function_dict = function_dict
        self._header = header
        self._footer = footer
        self.disabled = disabled

    @staticmethod
    def _label(value: str) -> str:
        return " ".join(value.split("_")) + " "

    def compose(self):
        with Container(classes="app-grid-2"):
            yield Static(
                "Code snippets are automatically generated according to parameters "
                "input in the Features tab. Please modify each function with "
                "extreme precaution as it will directly command your machine.",
                classes="warning",
            )
            with VerticalScroll(classes="features-2"):
                yield Horizontal(
                    Static(
                        "Toggle code modification",
                        classes="feature-text",
                        id="static_toggle_code_modification",
                    ),
                    Switch(
                        False,
                        id="toggle_code_modification",
                        classes="important_toggle",
                        animate=False,
                    ),
                    classes="horizontal-layout",
                )
                for variable, value in self._main_variables.items():
                    if variable == "path_type":
                        continue
                    label = self._label(variable)
                    if isinstance(value, bool):
                        field = Switch(value=value, id=variable, animate=False)
                    else:
                        field = Input(
                            value=f"{value}",
                            placeholder=label,
                            id=variable,
                            type="number",
                            max_length=10,
                            valid_empty=False,
                        )
                    yield Horizontal(
                        Static(
                            label,
                            classes="feature-text",
                            id=f"static_{variable}",
                        ),
                        field,
                        classes="horizontal-layout",
                        id=f"horizontal_{variable}",
                    )
                yield Button("[b]Create", id="send-printer", disabled=True)
            with VerticalScroll(
                classes="event-text-2", disabled=True, id="event-text-2"
            ):
                yield Static("Header", classes="label", id="static_header")
                yield TextArea.code_editor(
                    self._header,
                    classes="features",
                    language="python",
                    id="header",
                )
                yield Static("Footer", classes="label", id="static_footer")
                yield TextArea.code_editor(
                    text=self._footer,
                    classes="features",
                    language="python",
                    id="footer",
                )
                for functions in self._function_dict.values():
                    for function, code in functions.items():
                        yield Static(
                            function.title(),
                            classes="label",
                            id=f"static_{function}",
                        )
                        yield TextArea.code_editor(
                            code,
                            classes="features",
                            language="python",
                            id=function,
                        )
