from selectolax.lexbor import LexborHTMLParser
import httpx
from typing import List, Dict, Tuple, Optional, Any

class MachineScraper:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.color_map = {
            '#28a745': 'beginner',
            '#ffc107': 'intermediate',
            '#dc3545': 'advanced'
        }

    async def get_machines(self, page: int = 1, level: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
        """Fetch machines and pagination info."""
        params: Dict[str, Any] = {"p": page}
        if level: 
            params["l"] = level
        
        response = await self.client.get("/machines/", params=params)
        parser = LexborHTMLParser(response.text)
        
        machines = []
        for row in parser.css("table.table-dark tbody tr"):
            name_node = row.css_first("h4.vmname a")
            if not name_node: 
                continue

            style_node = row.css_first("div[style*='border-top']")
            diff_hex = ""
            if style_node:
                raw_style = style_node.attributes.get("style")
                style = str(raw_style or "").lower()
                if "solid " in style:
                    diff_hex = style.split("solid ")[-1].replace(";", "").strip()

            os_type = "unknown"
            os_images = row.css("img")
            for img in os_images:
                src = str(img.attributes.get("src") or "").lower()
                title = str(img.attributes.get("title") or "").lower()
                
                if "linux" in src or "linux" in title:
                    os_type = "linux"
                    break
                elif "windows" in src or "windows" in title:
                    os_type = "windows"
                    break

            status = "TO HACK"
            badges = row.css("span.badge")
            for b in badges:
                text = b.text(strip=True).upper()
                if text in ["TO HACK", "DONE", "PWNED"]:
                    status = text
                    break
            
            machines.append({
                "name": name_node.text(strip=True),
                "creator": row.css_first("a.creator").text(strip=True),
                "size": row.css_first("p.size").text(strip=True),
                "difficulty": self.color_map.get(diff_hex, "unknown"),
                "os": os_type,
                "status": status
            })

        pages = f"{page}/?"
        pagination_items = parser.css("li.page-item.disabled a.page-link")
        for item in pagination_items:
            text = item.text(strip=True)
            if "/" in text:
                pages = text
                break
        
        return machines, pages