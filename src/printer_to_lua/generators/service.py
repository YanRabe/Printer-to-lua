"""Application-facing orchestration for profile generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Optional

from printer_to_lua.data.features import (
    default_features,
    features_dict,
    materials_features,
    quality_features,
)
from printer_to_lua.data.printer import main_variables, util_functions_text
from printer_to_lua.firmware.registry import firmware_templates
from printer_to_lua.generators.features import generate_features
from printer_to_lua.generators.materials import generate_profile
from printer_to_lua.generators.printer import generate_printer
from printer_to_lua.generators.templates import write_files, write_profile
from printer_to_lua.models.printer import PrinterConfig


@dataclass(frozen=True)
class GeneratedProfile:
    """Generated file contents before they are persisted."""

    features: str
    printer: str
    quality: str
    material: str

    def files(self, quality_name: str = "low", material_name: str = "PLA") -> dict[str, str]:
        """Return the profile contents using the IceSL directory layout."""
        return {
            "features.lua": self.features,
            "printer.lua": self.printer,
            f"profiles/{quality_name}.lua": self.quality,
            f"materials/{material_name}.lua": self.material,
        }


class GenerationService:
    """Generate and persist all files for one printer configuration."""

    def generate(
        self,
        config: PrinterConfig,
        created_on: Optional[date] = None,
    ) -> GeneratedProfile:
        """Generate all profile content without touching the filesystem."""
        return GeneratedProfile(
            features=generate_features(
                config, default_features, features_dict, created_on
            ),
            printer=generate_printer(
                config,
                main_variables,
                util_functions_text,
                self._printer_templates(),
                created_on,
            ),
            quality=generate_profile(config, "quality", quality_features, created_on),
            material=generate_profile(
                config, "material", materials_features, created_on
            ),
        )

    def write(
        self,
        output_dir: Path,
        config: PrinterConfig,
        quality_name: str = "low",
        material_name: str = "PLA",
        created_on: Optional[date] = None,
    ) -> Path:
        """Generate and write a complete profile tree."""
        generated = self.generate(config, created_on)
        return write_profile(
            output_dir,
            config.require_name(),
            generated.files(quality_name, material_name),
        )

    def write_artifact(
        self,
        output_dir: Path,
        config: PrinterConfig,
        artifact: str,
        quality_name: str = "low",
        material_name: str = "PLA",
        created_on: Optional[date] = None,
    ) -> Path:
        """Generate and write one artifact while preserving the UI button scope."""
        generated = self.generate(config, created_on)
        files = generated.files(quality_name, material_name)
        artifact_files = {
            "features": {"features.lua": files["features.lua"]},
            "quality": {f"profiles/{quality_name}.lua": files[f"profiles/{quality_name}.lua"]},
            "material": {f"materials/{material_name}.lua": files[f"materials/{material_name}.lua"]},
            "printer": {"printer.lua": files["printer.lua"]},
        }
        try:
            selected = artifact_files[artifact]
        except KeyError as error:
            raise ValueError(f"Unknown profile artifact: {artifact}.") from error
        return write_files(output_dir, config.require_name(), selected)

    @staticmethod
    def _printer_templates() -> dict[str, Any]:
        """Adapt the registry to the printer generator's header contract."""
        result: dict[str, Any] = {}
        for firmware, name in ((0, "marlin"), (1, "reprap"), (2, "klipper")):
            templates = firmware_templates(firmware)
            result[name] = templates
        return result
