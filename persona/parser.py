
import re
from typing import Dict, Any, List, Optional

class PersonaParser:
    def _format_multiline_item(self, item_block: str) -> str:
        lines = [line.strip() for line in item_block.strip().split('\n')]
        if not lines: return ""
        title = lines[0].replace('**', '').strip()
        description = " ".join(lines[1:]).strip()
        return f"<strong>{title}</strong><br>{description}"

    def parse(self, username: str, text: str, avatar_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Takes the generated text and an avatar_url and converts them into a dictionary.
        """
        persona: Dict[str, Any] = {"username": username}

        quote_match = re.search(r'"([^"]+)"', text)
        persona["summary"] = quote_match.group(1) if quote_match else "No summary generated."

        # Use the real avatar_url if available, otherwise create a placeholder
        if avatar_url:
            persona["image_url"] = avatar_url
        else:
            persona["image_url"] = f"https://placehold.co/400x500/EFEFEF/333333?text={username[0].upper()}"

        persona["basic_info"] = self._extract_key_value_section(text, "BASIC INFORMATION")
        persona["motivations"] = self._extract_scored_section(text, "MOTIVATIONS")
        persona["personality"] = self._extract_scored_section(text, "PERSONALITY")
        persona["habits"] = self._extract_multiline_list_section(text, "BEHAVIOUR & HABITS")
        persona["frustrations"] = self._extract_multiline_list_section(text, "FRUSTRATIONS")
        persona["goals_needs"] = self._extract_multiline_list_section(text, "GOALS & NEEDS")

        return persona

    def _get_section_text(self, text: str, section_title: str) -> str:
        pattern = re.compile(rf"^{re.escape(section_title)}.*?\n-+\n(.*?)\n(?:-{{10,}}|\Z)", re.DOTALL | re.MULTILINE)
        match = pattern.search(text)
        return match.group(1).strip() if match else ""

    def _extract_multiline_list_section(self, text: str, section_title: str) -> List[str]:
        section_text = self._get_section_text(text, section_title)
        if not section_text: return []
        item_blocks = re.split(r'\n\s*-\s*', section_text)
        if item_blocks and item_blocks[0].startswith('- '):
            item_blocks[0] = item_blocks[0][2:]
        return [self._format_multiline_item(block) for block in item_blocks if block.strip()]

    def _extract_key_value_section(self, text: str, section_title: str) -> Dict[str, str]:
        section_text = self._get_section_text(text, section_title)
        if not section_text: return {}
        pattern = re.compile(r"-\s(.*?):\s(.*?)(?=\n-\s|\Z)", re.DOTALL)
        return {key.strip(): value.strip().replace("\n", " ") for key, value in pattern.findall(section_text)}

    def _extract_scored_section(self, text: str, section_title: str) -> Dict[str, int]:
        section_text = self._get_section_text(text, section_title)
        if not section_text: return {}
        pattern = re.compile(r"-\s(.*?):\s*\(?(\d{1,3})\)?", re.MULTILINE)
        scored_data = {}
        for match in pattern.finditer(section_text):
            scored_data[match.group(1).strip()] = int(match.group(2))
        return scored_data