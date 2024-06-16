import enum
import os
import typing

import keyboard
from pydantic import BaseModel, ValidationError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config.loader import IniConfigLoader
from src.config.models import HIDE_FROM_GUI_KEY, IS_HOTKEY_KEY

CONFIG_TABNAME = "Config"


def _validate_and_save_changes(model, header, key, value, method_to_reset_value: typing.Callable = None):
    try:
        setattr(model, key, value)
        IniConfigLoader().save_value(header, key, value)
        return True
    except ValidationError as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        message = f"There was an error setting {key} to {value}. See error below.\n\n"
        if method_to_reset_value:
            message = message + "Your value has been reset to its previous version.\n\n"
            method_to_reset_value(str(getattr(model, key)))
        message = message + str(e)
        msg.setText(message)
        msg.setWindowTitle("Error validating value")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        return False


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.model_to_parameter_value_map = {}
        layout = QVBoxLayout(self)
        scrollable_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scrollable_layout.addWidget(self._setup_reset_button())
        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().general, "General", "general"))
        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().char, "Character", "char"))
        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().advanced_options, "Advanced", "advanced_options"))
        scroll_widget.setLayout(scrollable_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        instructions_label = QLabel("Instructions")
        layout.addWidget(instructions_label)

        instructions_text = QTextBrowser()
        instructions_text.setOpenExternalLinks(True)
        instructions_text.append(
            "All values are saved automatically immediately upon changing. Hover over any label/field to see a brief "
            "description of what it is for. To read more about each parameter, please view "
            "<a href='https://github.com/aeon0/d4lf?tab=readme-ov-file#configs'>the config portion of the readme</a>"
        )
        instructions_text.append("")
        instructions_text.append(
            "Note: You will need to restart d4lf after modifying these values. Modifying params.ini manually while this gui is running is not supported (and really not necessary)."
        )

        instructions_text.setFixedHeight(100)
        layout.addWidget(instructions_text)

        self.setLayout(layout)

    def _generate_params_section(self, model: BaseModel, section_readable_header: str, section_config_header: str):
        group_box = QGroupBox(section_readable_header)
        form_layout = QFormLayout()

        all_parameter_metadata = model.model_json_schema()["properties"]

        for parameter in model:
            config_key, config_value = parameter
            parameter_metadata = all_parameter_metadata[config_key]

            hide_from_gui = parameter_metadata.get(HIDE_FROM_GUI_KEY)
            if hide_from_gui:
                continue
            description_text = parameter_metadata.get("description")
            is_hotkey = parameter_metadata.get(IS_HOTKEY_KEY)
            parameter_value_widget = self._generate_parameter_value_widget(
                model, section_config_header, config_key, config_value, is_hotkey
            )
            self.model_to_parameter_value_map[section_config_header + "." + config_key] = parameter_value_widget
            config_with_desc = QLabel(config_key)
            if description_text:
                # The span is a hack to make the tooltip wordwrap
                config_with_desc.setToolTip("<span>" + description_text + "</span>")
                parameter_value_widget.setToolTip("<span>" + description_text + "</span>")
            form_layout.addRow(config_with_desc, parameter_value_widget)

        group_box.setLayout(form_layout)
        return group_box

    @staticmethod
    def _generate_parameter_value_widget(model: BaseModel, section_config_header, config_key, config_value, is_hotkey):
        if config_key == "check_chest_tabs":
            parameter_value_widget = QChestTabWidget(model, section_config_header, config_key, config_value)
        elif config_key == "profiles":
            parameter_value_widget = QProfilesWidget(model, section_config_header, config_key, config_value)
        elif is_hotkey:
            parameter_value_widget = QHotkeyWidget(model, section_config_header, config_key, config_value)
        elif isinstance(config_value, enum.StrEnum):
            parameter_value_widget = IgnoreScrollWheelComboBox()
            enum_type = type(config_value)
            parameter_value_widget.addItems(list(enum_type))
            parameter_value_widget.setCurrentText(config_value)
            parameter_value_widget.currentTextChanged.connect(
                lambda: _validate_and_save_changes(model, section_config_header, config_key, parameter_value_widget.currentText())
            )
        elif isinstance(config_value, bool):
            parameter_value_widget = QCheckBox()
            parameter_value_widget.setChecked(config_value)
            parameter_value_widget.stateChanged.connect(
                lambda: _validate_and_save_changes(model, section_config_header, config_key, str(parameter_value_widget.isChecked()))
            )
        else:
            parameter_value_widget = QLineEdit(str(config_value))
            parameter_value_widget.editingFinished.connect(
                lambda: _validate_and_save_changes(
                    model,
                    section_config_header,
                    config_key,
                    parameter_value_widget.text(),
                    method_to_reset_value=parameter_value_widget.setText,
                )
            )

        return parameter_value_widget

    def reset_button_click(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        message = "This will reset all custom values in your params.ini to their default value. Are you sure you want to continue?"
        msg.setText(message)
        msg.setWindowTitle("Reset to default values?")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        result = msg.exec()  # Store the result of msg.exec()

        if result == QMessageBox.StandardButton.Ok:
            IniConfigLoader().load(clear=True)
            self._reset_values_for_model(IniConfigLoader().general, "general")
            self._reset_values_for_model(IniConfigLoader().char, "char")
            self._reset_values_for_model(IniConfigLoader().advanced_options, "advanced_options")


    def _reset_values_for_model(self, model, section_config_header):
        for parameter in model:
            config_key, config_value = parameter
            parameter_value_widget = self.model_to_parameter_value_map.get(section_config_header + "." + config_key)
            # Should always exist but just being safe
            if parameter_value_widget is None:
                continue

            if isinstance(parameter_value_widget, QChestTabWidget | QProfilesWidget | QHotkeyWidget):
                parameter_value_widget.reset_values(config_value)
            elif isinstance(parameter_value_widget, IgnoreScrollWheelComboBox):
                parameter_value_widget.setCurrentText(config_value)
            elif isinstance(parameter_value_widget, QCheckBox):
                parameter_value_widget.setChecked(config_value)
            else:
                parameter_value_widget.setText(str(config_value))

    def _setup_reset_button(self) -> QPushButton:
        reset_button = QPushButton("Reset to defaults")
        reset_button.clicked.connect(self.reset_button_click)
        return reset_button


class IgnoreScrollWheelComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, event)

        return event.ignore()


class QChestTabWidget(QWidget):
    def __init__(self, model, section_header, config_key, chest_tab_config: list[int]):
        super().__init__()
        self.all_checkboxes: list[QCheckBox] = []
        stash_checkbox_layout = QHBoxLayout()
        stash_checkbox_layout.setContentsMargins(0, 0, 0, 0)
        for x in range(6):
            stash_checkbox = QCheckBox(self)
            stash_checkbox.setText(str(x + 1))
            self.all_checkboxes.append(stash_checkbox)
            if x in chest_tab_config:
                stash_checkbox.setChecked(True)
            stash_checkbox.stateChanged.connect(lambda: self._save_changes_on_box_change(model, section_header, config_key))
            stash_checkbox_layout.addWidget(stash_checkbox)

        self.setLayout(stash_checkbox_layout)

    def reset_values(self, chest_tab_config: list[int]):
        for check_box in self.all_checkboxes:
            check_box.setChecked(int(check_box.text()) - 1 in chest_tab_config)

    def _save_changes_on_box_change(self, model, section_header, config_key):
        active_tabs = [check_box.text() for check_box in self.all_checkboxes if check_box.isChecked()]
        _validate_and_save_changes(model, section_header, config_key, ",".join(active_tabs), self.reset_values)


class QProfilesWidget(QWidget):
    def __init__(self, model, section_header, config_key, current_profiles):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.current_profile_line_edit = QLineEdit()
        self.reset_values(current_profiles)
        self.current_profile_line_edit.setReadOnly(True)
        layout.addWidget(self.current_profile_line_edit)

        open_picker_button = QPushButton()
        open_picker_button.setText("...")
        open_picker_button.setMinimumWidth(20)
        open_picker_button.clicked.connect(
            lambda: self._launch_picker(model, section_header, config_key, self.current_profile_line_edit.text().split(", "))
        )
        layout.addWidget(open_picker_button)

        self.setLayout(layout)

    def reset_values(self, current_profiles):
        self.current_profile_line_edit.setText(", ".join(current_profiles))

    def _launch_picker(self, model, section_header, config_key, current_profiles):
        profile_picker = QProfilePicker(self, current_profiles)
        if profile_picker.exec():
            selected_profiles = ", ".join(profile_picker.get_selected_profiles())
            _validate_and_save_changes(
                model,
                section_header,
                config_key,
                selected_profiles,
                self.current_profile_line_edit.setText,
            )
            self.current_profile_line_edit.setText(selected_profiles)


class QProfilePicker(QDialog):
    def __init__(self, parent, current_profiles):
        super().__init__(parent)
        self.setWindowTitle("Select profiles")

        overall_layout = QVBoxLayout()
        self.setGeometry(100, 100, 400, 400)

        profile_folder = IniConfigLoader().user_dir / "profiles"
        if not os.path.exists(profile_folder):
            os.makedirs(profile_folder)

        all_profile_files = os.listdir(profile_folder)
        all_profiles = [os.path.splitext(profile_file)[0] for profile_file in all_profile_files]

        unactivated_profiles_list_widget = QListWidget()
        unactivated_profiles_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        unactivated_profiles_list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        unactivated_profiles_list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.activated_profiles_list_widget = QListWidget()
        self.activated_profiles_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.activated_profiles_list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.activated_profiles_list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

        for profile_name in all_profiles:
            if profile_name not in current_profiles:
                QListWidgetItem(profile_name, unactivated_profiles_list_widget)

        for profile_name in current_profiles:
            # Filter out any examples or defaults that don't have a file
            if profile_name in all_profiles:
                QListWidgetItem(profile_name, self.activated_profiles_list_widget)

        list_widget_layout = QGridLayout()
        list_widget_layout.addWidget(QLabel("Unactivated Profiles"), 0, 0)
        list_widget_layout.addWidget(unactivated_profiles_list_widget, 1, 0)
        list_widget_layout.addWidget(QLabel("Activated Profiles"), 0, 1)
        list_widget_layout.addWidget(self.activated_profiles_list_widget, 1, 1)

        overall_layout.addLayout(list_widget_layout)

        message = QTextEdit(
            f"On the left are all unactivated profiles found in {profile_folder}. On the right are currently active "
            f"profiles. Drag and drop from the left to the right to activate the profile. You can change order by"
            f" dragging a profile up and down in the right list."
        )
        message.setReadOnly(True)
        message.setFixedHeight(100)
        overall_layout.addWidget(message)

        ok_cancel_buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(ok_cancel_buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        overall_layout.addWidget(self.buttonBox)
        self.setLayout(overall_layout)

    def get_selected_profiles(self):
        return [self.activated_profiles_list_widget.item(x).text() for x in range(self.activated_profiles_list_widget.count())]


class QHotkeyWidget(QWidget):
    def __init__(self, model, section_header, config_key, current_value):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.open_picker_button = QPushButton()
        self.reset_values(current_value)
        self.open_picker_button.clicked.connect(lambda: self._launch_hotkey_dialog(model, section_header, config_key))
        self.open_picker_button.setStyleSheet("text-align:left;padding-left: 5px;")
        layout.addWidget(self.open_picker_button)

        self.setLayout(layout)

    def reset_values(self, current_value):
        self.open_picker_button.setText(current_value)

    def _launch_hotkey_dialog(self, model, section_header, config_key):
        hotkey_dialog = HotkeyListenerDialog(self)
        if hotkey_dialog.exec():
            new_hotkey = hotkey_dialog.get_hotkey()
            if new_hotkey and _validate_and_save_changes(model, section_header, config_key, new_hotkey):
                self.open_picker_button.setText(new_hotkey)


class HotkeyListenerDialog(QDialog):
    def __init__(self, parent=None, hotkey=""):
        super().__init__(parent)
        self.setWindowTitle("Set Hotkey")
        self.hotkey = hotkey

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Press the key or combination of keys you\nwant to use as a hotkey, then click save.", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hotkey_label = QLabel(self.hotkey, self)
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.hotkey_label)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)

    def keyPressEvent(self, event):
        modifiers_str = []
        for modifier in event.modifiers():
            if modifier == Qt.KeyboardModifier.ShiftModifier:
                modifiers_str.append("shift")
            elif modifier == Qt.KeyboardModifier.ControlModifier:
                modifiers_str.append("ctrl")
            elif modifier == Qt.KeyboardModifier.AltModifier:
                modifiers_str.append("alt")

        native_virtual_key = event.nativeVirtualKey()
        non_mod_key, _ = keyboard._winkeyboard.official_virtual_keys.get(native_virtual_key)
        if non_mod_key in modifiers_str:
            non_mod_key = ""

        key_str = " + ".join(modifiers_str + [non_mod_key])
        self.hotkey = key_str
        self.hotkey_label.setText(key_str)

    def get_hotkey(self):
        return self.hotkey
