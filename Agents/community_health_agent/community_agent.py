from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

from .config import CommunityAgentConfig
from .message_templates import MessageTemplateContext, SeverityLevel


# --- LLM interface and a simple dummy implementation -------------------------


class LLMClient(Protocol):
    """
    Abstract interface for any small LLM you want to use
    (OpenAI, local model, etc.).
    """

    def generate_text(self, prompt: str, *, system: str | None = None) -> str: ...


class TemplateLLMClient:
    """
    Simple non-API implementation with multilingual support using built-in translations.

    You can replace this with a real LLM client later, e.g.:

        class OpenAILLMClient:
            def __init__(self, client):
                self.client = client

            def generate_text(self, prompt: str, *, system: str | None = None) -> str:
                # call your OpenAI / LLaMA endpoint here
                ...

    """

    # Translation dictionary for common health advisory terms
    TRANSLATIONS = {
        "en": {
            "summary": "Summary",
            "recommendations": "Recommendations",
            "actions": "Recommended Actions",
            "vulnerable": "Vulnerable Groups",
            "stay_informed": "Stay Informed",
            "public_health_advisory": "Public Health Advisory",
        },
        "hi": {
            "summary": "सारांश",
            "recommendations": "सिफारिशें",
            "actions": "अनुशंसित कार्य",
            "vulnerable": "कमजोर समूह",
            "stay_informed": "सूचित रहें",
            "public_health_advisory": "सार्वजनिक स्वास्थ्य सलाह",
        },
        "es": {
            "summary": "Resumen",
            "recommendations": "Recomendaciones",
            "actions": "Acciones Recomendadas",
            "vulnerable": "Grupos Vulnerables",
            "stay_informed": "Manténgase Informado",
            "public_health_advisory": "Aviso de Salud Pública",
        },
        "fr": {
            "summary": "Résumé",
            "recommendations": "Recommandations",
            "actions": "Actions Recommandées",
            "vulnerable": "Groupes Vulnérables",
            "stay_informed": "Restez Informé",
            "public_health_advisory": "Avis de Santé Publique",
        },
        "ta": {
            "summary": "சுருக்கம்",
            "recommendations": "பரிந்துரைகள்",
            "actions": "பரிந்துரைக்கப்பட்ட நடவடிக்கைகள்",
            "vulnerable": "பாதிக்கப்படக்கூடிய குழுக்கள்",
            "stay_informed": "தெரிந்து கொள்ளவும்",
            "public_health_advisory": "பொது சுகாதார ஆலோசனை",
        },
    }

    def generate_text(self, prompt: str, *, system: str | None = None, language: str = "en") -> str:
        """Generate multilingual health advisory text based on language parameter."""
        # Extract language from prompt if available
        if "Language: " in prompt:
            lang_line = [line for line in prompt.split("\n") if "Language: " in line]
            if lang_line:
                language = lang_line[0].replace("Language: ", "").strip().lower()
        
        # Get translations for the language, default to English if not available
        trans = self.TRANSLATIONS.get(language, self.TRANSLATIONS["en"])
        
        # Generate language-appropriate advisory
        advisory_header = trans.get("public_health_advisory", "Public Health Advisory")
        actions_header = trans.get("actions", "Recommended Actions")
        vulnerable_header = trans.get("vulnerable", "Vulnerable Groups")
        stay_informed = trans.get("stay_informed", "Stay Informed")
        
        # Parse severity from prompt
        severity_line = [line for line in prompt.split("\n") if "Severity level: " in line]
        severity = severity_line[0].replace("Severity level: ", "").strip() if severity_line else "ADVISORY"
        
        # Build language-specific response
        response_parts = [
            f"═══ {advisory_header} ═══\n",
            f"⚠️ {severity}\n\n"
        ]
        
        # Add severity-specific opening message based on language
        severity_messages = {
            "en": {
                "INFO": "General Health Information",
                "ADVISORY": "Health Advisory - Please Take Note",
                "ALERT": "Health Alert - Action Required",
                "EMERGENCY": "EMERGENCY - Immediate Action Needed"
            },
            "hi": {
                "INFO": "सामान्य स्वास्थ्य जानकारी",
                "ADVISORY": "स्वास्थ्य सलाह - कृपया ध्यान दें",
                "ALERT": "स्वास्थ्य चेतावनी - कार्रवाई आवश्यक है",
                "EMERGENCY": "आपातकाल - तुरंत कार्रवाई आवश्यक है"
            },
            "es": {
                "INFO": "Información General de Salud",
                "ADVISORY": "Aviso de Salud - Tenga en Cuenta",
                "ALERT": "Alerta de Salud - Se Requiere Acción",
                "EMERGENCY": "EMERGENCIA - Se Requiere Acción Inmediata"
            },
            "fr": {
                "INFO": "Information Générale sur la Santé",
                "ADVISORY": "Avis de Santé - Veuillez Prendre Note",
                "ALERT": "Alerte Sanitaire - Action Requise",
                "EMERGENCY": "URGENCE - Action Immédiate Requise"
            },
            "ta": {
                "INFO": "பொது சுகாதார தகவல்",
                "ADVISORY": "சுகாதார ஆலோசனை - தயவுசெய்து கவனிக்கவும்",
                "ALERT": "சுகாதார எச்சரிக்கை - நடவடிக்கை தேவை",
                "EMERGENCY": "அவசரநிலை - உடனடி நடவடிக்கை தேவை"
            }
        }
        
        severity_msgs = severity_messages.get(language, severity_messages["en"])
        response_parts.append(f"{severity_msgs.get(severity, severity)}\n\n")
        
        # Add recommendations header
        response_parts.append(f"📋 {actions_header}:\n")
        response_parts.append("• Stay vigilant about health indicators\n")
        response_parts.append("• Follow local health authority guidelines\n")
        response_parts.append("• Practice preventive hygiene measures\n\n")
        
        # Add vulnerable groups information
        response_parts.append(f"👥 {vulnerable_header}:\n")
        response_parts.append("• Children and elderly individuals\n")
        response_parts.append("• People with chronic conditions\n")
        response_parts.append("• Immunocompromised individuals\n\n")
        
        # Add stay informed message
        stay_informed_msgs = {
            "en": "Monitor local health department updates and follow their guidance.",
            "hi": "स्थानीय स्वास्थ्य विभाग के अपडेट की निगरानी करें और उनके मार्गदर्शन का पालन करें।",
            "es": "Monitoree las actualizaciones del departamento de salud local y siga sus orientaciones.",
            "fr": "Surveillez les mises à jour du ministère de la santé local et suivez leurs orientations.",
            "ta": "உள்ளூர் சுகாதார திறைக்களத்தின் புதுப்பிப்புகளைக் கண்காணிக்கவும் மற்றும் அவற்றின் வழிகாட்டுதலை பின்பற்றவும்।"
        }
        
        response_parts.append(f"ℹ️ {stay_informed}: {stay_informed_msgs.get(language, stay_informed_msgs['en'])}")
        
        return "\n".join(response_parts)


# --- Core data model ---------------------------------------------------------


@dataclass
class CommunityContext:
    """
    Structured inputs for the Community Health Agent.

    You can extend this with more risk factors later.
    """

    location_name: str
    languages: List[str]

    pollution_aqi: int | None = None
    resp_case_trend: str | None = None  # 'stable' | 'rising' | 'falling'
    outbreak_risk: float | None = None  # 0.0–1.0
    outbreak_type: str | None = None
    heat_index: float | None = None
    flood_risk: float | None = None     # 0.0–1.0

    notes: str | None = None


# --- Core agent --------------------------------------------------------------


class CommunityHealthAgent:
    """
    Generates public health advisories based on community-level signals.

    - Uses simple RULES to determine severity.
    - Uses an LLM (or the TemplateLLMClient) to generate multilingual messages.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        config: CommunityAgentConfig | None = None,
    ) -> None:
        self.config = config or CommunityAgentConfig()
        self.llm_client: LLMClient = llm_client or TemplateLLMClient()

    # ---------------------- Public API ---------------------------------------

    def generate_advisory(self, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entrypoint.

        raw_context: dict, will be converted into CommunityContext.
        Returns: dict with severity, reasons, recommended channels and messages.
        """
        ctx = self._parse_context(raw_context)
        severity, reasons = self._classify_severity(ctx)
        channels = self._recommend_channels(severity)
        messages = self._generate_messages(ctx, severity, reasons)

        return {
            "severity": severity.value,
            "reasons": reasons,
            "recommended_channels": channels,
            "messages": messages,
        }

    # ---------------------- Internal helpers ---------------------------------

    def _parse_context(self, data: Dict[str, Any]) -> CommunityContext:
        languages = data.get("languages") or self.config.default_languages
        location = data.get("location_name") or self.config.default_location_name

        return CommunityContext(
            location_name=location,
            languages=list(languages),
            pollution_aqi=data.get("pollution_aqi"),
            resp_case_trend=data.get("resp_case_trend"),
            outbreak_risk=data.get("outbreak_risk"),
            outbreak_type=data.get("outbreak_type"),
            heat_index=data.get("heat_index"),
            flood_risk=data.get("flood_risk"),
            notes=data.get("notes"),
        )

    def _classify_severity(self, ctx: CommunityContext) -> tuple[SeverityLevel, List[str]]:
        """
        Simple rule-based severity classifier with multilingual support.
        """
        cfg = self.config
        reasons: List[str] = []
        level = SeverityLevel.INFO
        
        # Get primary language for reasons text
        primary_lang = ctx.languages[0] if ctx.languages else "en"

        # Translation dictionaries for reasons
        translations = {
            "en": {
                "aqi_emergency": f"AQI is extremely poor",
                "aqi_alert": f"AQI is very poor",
                "aqi_advisory": f"AQI is moderate to unhealthy",
                "outbreak_emergency": f"Very high outbreak risk score",
                "outbreak_alert": f"High outbreak risk score",
                "outbreak_advisory": f"Moderate outbreak risk score",
                "heat_emergency": f"Extreme heat index of",
                "heat_alert": f"Very high heat index of",
                "heat_advisory": f"High heat index of",
                "flood_emergency": "Extreme flood risk in the area.",
                "flood_alert": "High flood risk in the area.",
                "flood_advisory": "Moderate flood risk in the area.",
                "resp_rising": "Respiratory cases are rising in clinics and hospitals.",
                "no_risks": "No major risks detected, sending general health information.",
            },
            "hi": {
                "aqi_emergency": f"वायु गुणवत्ता अत्यंत खराब है",
                "aqi_alert": f"वायु गुणवत्ता बहुत खराब है",
                "aqi_advisory": f"वायु गुणवत्ता मध्यम से अस्वास्थ्यकर है",
                "outbreak_emergency": f"बहुत अधिक प्रकोप जोखिम स्कोर",
                "outbreak_alert": f"उच्च प्रकोप जोखिम स्कोर",
                "outbreak_advisory": f"मध्यम प्रकोप जोखिम स्कोर",
                "heat_emergency": f"अत्यधिक गर्मी सूचकांक",
                "heat_alert": f"बहुत अधिक गर्मी सूचकांक",
                "heat_advisory": f"उच्च गर्मी सूचकांक",
                "flood_emergency": "क्षेत्र में चरम बाढ़ का खतरा है।",
                "flood_alert": "क्षेत्र में उच्च बाढ़ का खतरा है।",
                "flood_advisory": "क्षेत्र में मध्यम बाढ़ का खतरा है।",
                "resp_rising": "क्लीनिकों और अस्पतालों में श्वसन रोग के मामले बढ़ रहे हैं।",
                "no_risks": "कोई प्रमुख जोखिम नहीं पाया गया, सामान्य स्वास्थ्य जानकारी भेजी जा रही है।",
            },
            "es": {
                "aqi_emergency": f"La calidad del aire es extremadamente pobre",
                "aqi_alert": f"La calidad del aire es muy pobre",
                "aqi_advisory": f"La calidad del aire es moderada a poco saludable",
                "outbreak_emergency": f"Puntuación de riesgo de brote muy alta",
                "outbreak_alert": f"Puntuación de riesgo de brote alta",
                "outbreak_advisory": f"Puntuación de riesgo de brote moderada",
                "heat_emergency": f"Índice de calor extremo",
                "heat_alert": f"Índice de calor muy alto",
                "heat_advisory": f"Índice de calor alto",
                "flood_emergency": "Riesgo de inundación extrema en el área.",
                "flood_alert": "Riesgo de inundación alto en el área.",
                "flood_advisory": "Riesgo de inundación moderado en el área.",
                "resp_rising": "Los casos respiratorios están aumentando en clínicas y hospitales.",
                "no_risks": "No se detectaron riesgos importantes, se envía información general de salud.",
            }
        }
        
        trans = translations.get(primary_lang, translations["en"])

        # Pollution
        if ctx.pollution_aqi is not None:
            if ctx.pollution_aqi >= cfg.aqi_emergency:
                level = SeverityLevel.EMERGENCY
                reasons.append(f"{trans['aqi_emergency']} ({ctx.pollution_aqi}).")
            elif ctx.pollution_aqi >= cfg.aqi_alert:
                level = max(level, SeverityLevel.ALERT, key=self._severity_rank)
                reasons.append(f"{trans['aqi_alert']} ({ctx.pollution_aqi}).")
            elif ctx.pollution_aqi >= cfg.aqi_advisory:
                level = max(level, SeverityLevel.ADVISORY, key=self._severity_rank)
                reasons.append(f"{trans['aqi_advisory']} ({ctx.pollution_aqi}).")

        # Outbreak risk
        if ctx.outbreak_risk is not None:
            if ctx.outbreak_risk >= cfg.outbreak_emergency:
                level = SeverityLevel.EMERGENCY
                outbreak_type = ctx.outbreak_type or ("संक्रामक रोग" if primary_lang == "hi" else "infectious disease")
                reasons.append(
                    f"{trans['outbreak_emergency']} ({ctx.outbreak_risk:.2f}) "
                    f"for {outbreak_type}."
                )
            elif ctx.outbreak_risk >= cfg.outbreak_alert:
                level = max(level, SeverityLevel.ALERT, key=self._severity_rank)
                reasons.append(f"{trans['outbreak_alert']} ({ctx.outbreak_risk:.2f}).")
            elif ctx.outbreak_risk >= cfg.outbreak_advisory:
                level = max(level, SeverityLevel.ADVISORY, key=self._severity_rank)
                reasons.append(f"{trans['outbreak_advisory']} ({ctx.outbreak_risk:.2f}).")

        # Heat index
        if ctx.heat_index is not None:
            if ctx.heat_index >= cfg.heat_index_emergency:
                level = SeverityLevel.EMERGENCY
                reasons.append(f"{trans['heat_emergency']} {ctx.heat_index:.1f}°C.")
            elif ctx.heat_index >= cfg.heat_index_alert:
                level = max(level, SeverityLevel.ALERT, key=self._severity_rank)
                reasons.append(f"{trans['heat_alert']} {ctx.heat_index:.1f}°C.")
            elif ctx.heat_index >= cfg.heat_index_advisory:
                level = max(level, SeverityLevel.ADVISORY, key=self._severity_rank)
                reasons.append(f"{trans['heat_advisory']} {ctx.heat_index:.1f}°C.")

        # Flood risk
        if ctx.flood_risk is not None:
            if ctx.flood_risk >= cfg.flood_risk_emergency:
                level = SeverityLevel.EMERGENCY
                reasons.append(trans['flood_emergency'])
            elif ctx.flood_risk >= cfg.flood_risk_alert:
                level = max(level, SeverityLevel.ALERT, key=self._severity_rank)
                reasons.append(trans['flood_alert'])
            elif ctx.flood_risk >= cfg.flood_risk_advisory:
                level = max(level, SeverityLevel.ADVISORY, key=self._severity_rank)
                reasons.append(trans['flood_advisory'])

        # Respiratory case trend
        if ctx.resp_case_trend == "rising":
            level = max(level, SeverityLevel.ADVISORY, key=self._severity_rank)
            reasons.append(trans['resp_rising'])

        if not reasons:
            reasons.append(trans['no_risks'])

        return level, reasons

    @staticmethod
    def _severity_rank(level: SeverityLevel) -> int:
        order = {
            SeverityLevel.INFO: 0,
            SeverityLevel.ADVISORY: 1,
            SeverityLevel.ALERT: 2,
            SeverityLevel.EMERGENCY: 3,
        }
        return order[level]

    def _recommend_channels(self, severity: SeverityLevel) -> List[str]:
        if severity == SeverityLevel.EMERGENCY:
            return ["SMS", "WhatsApp", "Loudspeaker", "Local TV/Radio"]
        if severity == SeverityLevel.ALERT:
            return ["SMS", "WhatsApp", "Social Media", "Posters"]
        if severity == SeverityLevel.ADVISORY:
            return ["WhatsApp", "Social Media", "Posters"]
        return ["Social Media"]

    def _generate_messages(
        self,
        ctx: CommunityContext,
        severity: SeverityLevel,
        reasons: List[str],
    ) -> Dict[str, str]:
        """
        Call the LLM (or dummy template LLM) for each language.
        """
        template_ctx = MessageTemplateContext(
            location_name=ctx.location_name,
            severity=severity,
            reasons=reasons,
            languages=ctx.languages,
            notes=ctx.notes,
        )

        system = template_ctx.build_system_instruction()
        result: Dict[str, str] = {}

        for lang in ctx.languages:
            prompt = template_ctx.build_user_prompt(lang)
            # Pass language parameter to LLM client for language-specific generation
            if hasattr(self.llm_client, 'generate_text'):
                # Check if the method accepts language parameter
                import inspect
                sig = inspect.signature(self.llm_client.generate_text)
                if 'language' in sig.parameters:
                    text = self.llm_client.generate_text(prompt=prompt, system=system, language=lang)
                else:
                    text = self.llm_client.generate_text(prompt=prompt, system=system)
            else:
                text = self.llm_client.generate_text(prompt=prompt, system=system)
            result[lang] = text

        return result


# --- Simple CLI demo ---------------------------------------------------------


def demo() -> None:
    agent = CommunityHealthAgent()

    example = {
        "location_name": "Nagpur",
        "languages": ["en", "hi"],
        "pollution_aqi": 210,
        "resp_case_trend": "rising",
        "outbreak_risk": 0.65,
        "outbreak_type": "dengue",
        "heat_index": 41.0,
        "flood_risk": 0.2,
        "notes": "School exams are ongoing, avoid panic messaging.",
    }

    result = agent.generate_advisory(example)
    print("Severity:", result["severity"])
    print("Reasons:")
    for r in result["reasons"]:
        print(" -", r)

    print("\nRecommended channels:", ", ".join(result["recommended_channels"]))
    print("\nMessages:")
    for lang, msg in result["messages"].items():
        print(f"\n--- [{lang}] ---\n{msg}\n")


if __name__ == "__main__":
    demo()
