"""
SEO SWARM - Reusable Terminal Widgets

Unicode box drawing characters, panels, tables, trees, and dividers.
Uses ANSI escape codes from the shared COLORS dictionary in dashboard.py.
Zero external dependencies — pure stdlib.
"""

from typing import List, Optional, Dict, Any
from seo_swarm.tui.dashboard import COLORS

# ══════════════════════════════════════════════════════════════════════════════
# Box drawing character sets
# ══════════════════════════════════════════════════════════════════════════════

BOX_CHARS: Dict[str, Dict[str, str]] = {
    "single": {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
        "lc": "╠", "rc": "╣", "tc": "╦", "bc": "╩",
        "x": "╬",
    },
    "double": {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
        "lc": "╠", "rc": "╣", "tc": "╦", "bc": "╩",
        "x": "╬",
    },
    "rounded": {
        "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
        "h": "─", "v": "│",
        "lc": "├", "rc": "┤", "tc": "┬", "bc": "┴",
        "x": "┼",
    },
    "bold": {
        "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛",
        "h": "━", "v": "┃",
        "lc": "┣", "rc": "┫", "tc": "┳", "bc": "┻",
        "x": "╋",
    },
    "dashed": {
        "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
        "h": "╌", "v": "┊",
        "lc": "├", "rc": "┤", "tc": "┬", "bc": "┴",
        "x": "┼",
    },
    "ascii": {
        "tl": "+", "tr": "+", "bl": "+", "br": "+",
        "h": "-", "v": "|",
        "lc": "+", "rc": "+", "tc": "+", "bc": "+",
        "x": "+",
    },
}

# Double-line set uses proper double-drawing characters
BOX_CHARS["double"] = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║",
    "lc": "╠", "rc": "╣", "tc": "╦", "bc": "╩",
    "x": "╬",
}

DIVIDER_CHARS: Dict[str, str] = {
    "single": "─",
    "double": "═",
    "bold": "━",
    "dashed": "╌",
    "dotted": "┅",
    "ascii": "-",
    "heavy": "▔",
}


# ══════════════════════════════════════════════════════════════════════════════
# Widgets
# ══════════════════════════════════════════════════════════════════════════════

class Box:
    """Styled box around content using Unicode box-drawing characters.

    Border styles: single, double, rounded, bold, dashed, ascii.

    Example:
        box = Box()
        print(box.render("Hello, World!", title="Greeting"))

    Output:
        ╔══ Greeting ═══════════╗
        ║ Hello, World!         ║
        ╚═══════════════════════╝
    """

    def __init__(
        self,
        border_style: str = "single",
        color: Optional[str] = None,
        padding: int = 1,
        min_width: int = 0,
    ):
        """Initialize a Box widget.

        Args:
            border_style: One of 'single', 'double', 'rounded', 'bold', 'dashed', 'ascii'.
            color: Optional ANSI color name from COLORS dict (e.g., 'cyan', 'bright_green').
            padding: Horizontal padding inside the box (spaces on each side).
            min_width: Minimum width of the box (excluding borders). Content is padded to this.
        """
        self.border_style = border_style
        self.color = color
        self.padding = padding
        self.min_width = min_width
        self._chars = BOX_CHARS.get(border_style, BOX_CHARS["single"])
        self._color_code = COLORS.get(color, "") if color else ""

    def render(self, text: str, title: str = "") -> str:
        """Render the box around the given text.

        Args:
            text: The content to place inside the box. May contain newlines.
            title: Optional title placed in the top-left of the border.

        Returns:
            A string containing the fully-rendered box with ANSI codes.
        """
        c = self._chars
        reset = COLORS["reset"]
        cc = self._color_code
        pad = " " * self.padding

        lines = text.split("\n")
        content_width = max((len(line) for line in lines), default=0)
        width = max(content_width + self.padding * 2, self.min_width)

        # Build top border with optional title
        top = self._build_top_border(c, cc, reset, width, title)

        # Build middle lines
        middle = []
        for line in lines:
            # Pad line to content_width then fill remaining space
            padded_line = line.ljust(content_width)
            remaining = width - content_width - self.padding * 2
            fill = " " * max(0, remaining)
            middle.append(f"{cc}{c['v']}{reset}{pad}{padded_line}{fill}{pad}{cc}{c['v']}{reset}")

        # Build bottom border
        bottom = f"{cc}{c['bl']}{c['h'] * (width + 2)}{c['br']}{reset}"

        return "\n".join([top] + middle + [bottom])

    def _build_top_border(self, c: Dict[str, str], cc: str, reset: str, width: int, title: str) -> str:
        """Build the top border line, optionally embedding a title."""
        total_h = width + 2  # total horizontal chars between corners

        if title:
            title_str = f" {title} "
            if len(title_str) >= total_h:
                title_str = title_str[:total_h]
            # Left side after title
            right_len = total_h - len(title_str)
            if right_len < 0:
                right_len = 0
            return f"{cc}{c['tl']}{title_str}{c['h'] * right_len}{c['tr']}{reset}"
        else:
            return f"{cc}{c['tl']}{c['h'] * total_h}{c['tr']}{reset}"


class Panel:
    """Panel with distinct header, body, and footer sections.

    Example:
        panel = Panel()
        print(panel.render("Dashboard", "System is healthy.", "v1.0.0"))

    Output:
        ╔══ Dashboard ═══════════════════╗
        ║                                ║
        ║  System is healthy.            ║
        ║                                ║
        ╟────────────────────────────────╢
        ║  v1.0.0                        ║
        ╚════════════════════════════════╝
    """

    def __init__(
        self,
        border_style: str = "single",
        header_style: str = "bold",
        color: Optional[str] = None,
        width: int = 60,
    ):
        """Initialize a Panel widget.

        Args:
            border_style: Border style for the outer box (single, double, rounded, etc.).
            header_style: Border style for the header/body separator line.
            color: Optional ANSI color name from COLORS dict.
            width: Fixed width of the panel (excluding borders).
        """
        self.border_style = border_style
        self.header_style = header_style
        self.color = color
        self.width = width
        self._chars = BOX_CHARS.get(border_style, BOX_CHARS["single"])
        self._sep_chars = BOX_CHARS.get(header_style, BOX_CHARS["single"])
        self._color_code = COLORS.get(color, "") if color else ""

    def render(self, header: str, body: str, footer: str = "") -> str:
        """Render a panel with header, body, and optional footer.

        Args:
            header: Text for the panel header (shown in top border).
            body: Main content. May contain newlines.
            footer: Optional footer text, separated by a horizontal rule.

        Returns:
            A string containing the fully-rendered panel.
        """
        c = self._chars
        sc = self._sep_chars
        reset = COLORS["reset"]
        cc = self._color_code
        w = self.width

        # Top border with header title
        lines = [self._header_line(c, cc, reset, w, header)]

        # Blank line after header
        lines.append(f"{cc}{c['v']}{reset}{' ' * w}{cc}{c['v']}{reset}")

        # Body lines (word-wrapped by simple newline split)
        for line in body.split("\n"):
            trimmed = line[:w]
            lines.append(f"{cc}{c['v']}{reset}  {trimmed.ljust(w - 2)}{cc}{c['v']}{reset}")

        # Footer separator and content
        if footer:
            lines.append(f"{cc}{sc['lc']}{sc['h'] * w}{sc['rc']}{reset}")
            for line in footer.split("\n"):
                trimmed = line[:w]
                lines.append(f"{cc}{c['v']}{reset}  {trimmed.ljust(w - 2)}{cc}{c['v']}{reset}")

        # Bottom border
        lines.append(f"{cc}{c['bl']}{c['h'] * w}{c['br']}{reset}")

        return "\n".join(lines)

    def _header_line(self, c: Dict[str, str], cc: str, reset: str, width: int, title: str) -> str:
        """Build the header line with embedded title."""
        title_str = f" {title} "
        if len(title_str) >= width:
            title_str = title_str[:width]
        right_len = width - len(title_str)
        if right_len < 0:
            right_len = 0
        return f"{cc}{c['tl']}{title_str}{c['h'] * right_len}{c['tr']}{reset}"


class Table:
    """ASCII table with headers, alignment, and auto-sized columns.

    Example:
        table = Table()
        table.set_headers(["Name", "Score", "Status"])
        table.add_row(["Alice", "95", "Pass"])
        table.add_row(["Bob", "72", "Pass"])
        print(table.render())
    """

    def __init__(self, border: bool = True, color: Optional[str] = None):
        """Initialize a Table.

        Args:
            border: Whether to draw outer and inner borders (False = simple aligned columns).
            color: Optional ANSI color name from COLORS dict.
        """
        self.border = border
        self.color = color
        self._color_code = COLORS.get(color, "") if color else ""
        self._headers: List[str] = []
        self._alignments: List[str] = []  # 'left', 'center', 'right'
        self._rows: List[List[str]] = []

    def set_headers(self, headers: List[str], alignments: Optional[List[str]] = None):
        """Set the table headers.

        Args:
            headers: List of header column names.
            alignments: Optional list of alignments ('left', 'center', 'right').
                        Defaults to 'left' for all columns.
        """
        self._headers = list(headers)
        if alignments:
            self._alignments = list(alignments)
        else:
            self._alignments = ["left"] * len(headers)

    def add_row(self, row: List[str]):
        """Add a data row to the table.

        Args:
            row: List of string values, one per column.
        """
        self._rows.append([str(v) for v in row])

    def render(self) -> str:
        """Render the table as a formatted string.

        Returns:
            A string containing the rendered table.
        """
        if not self._headers:
            return ""

        reset = COLORS["reset"]
        cc = self._color_code

        # Calculate column widths
        col_count = len(self._headers)
        widths = [len(h) for h in self._headers]
        for row in self._rows:
            for i, cell in enumerate(row):
                if i < col_count:
                    widths[i] = max(widths[i], len(cell))

        # Ensure alignments list matches columns
        while len(self._alignments) < col_count:
            self._alignments.append("left")

        lines: List[str] = []

        if self.border:
            # Top border
            sep_top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
            lines.append(f"{cc}{sep_top}{reset}")

            # Header
            header_cells = []
            for i, h in enumerate(self._headers):
                header_cells.append(f" {self._align_cell(h, widths[i])} ")
            lines.append(f"{cc}│{reset}" + f"{cc}│{reset}".join(header_cells) + f"{cc}│{reset}")

            # Header separator
            sep_mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
            lines.append(f"{cc}{sep_mid}{reset}")

            # Rows
            for row in self._rows:
                cells = []
                for i in range(col_count):
                    val = row[i] if i < len(row) else ""
                    cells.append(f" {self._align_cell(val, widths[i])} ")
                lines.append(f"{cc}│{reset}" + f"{cc}│{reset}".join(cells) + f"{cc}│{reset}")

            # Bottom border
            sep_bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
            lines.append(f"{cc}{sep_bot}{reset}")

        else:
            # No borders — simple aligned columns
            # Header
            header_cells = []
            for i, h in enumerate(self._headers):
                header_cells.append(self._align_cell(h, widths[i]))
            lines.append(f"{cc}" + "  ".join(header_cells) + f"{reset}")

            # Underline
            underline = "  ".join("─" * w for w in widths)
            lines.append(f"{cc}{underline}{reset}")

            # Rows
            for row in self._rows:
                cells = []
                for i in range(col_count):
                    val = row[i] if i < len(row) else ""
                    cells.append(self._align_cell(val, widths[i]))
                lines.append("  ".join(cells))

        return "\n".join(lines)

    @staticmethod
    def _align_cell(text: str, width: int, alignment: str = "left") -> str:
        """Align text within a fixed-width cell.

        Args:
            text: The text to align.
            width: The column width.
            alignment: 'left', 'center', or 'right'.

        Returns:
            Padded string of exactly `width` characters.
        """
        if alignment == "right":
            return text.rjust(width)
        elif alignment == "center":
            return text.center(width)
        else:
            return text.ljust(width)


class Tree:
    """Tree view with Unicode branch indicators (├ └ │).

    Example:
        tree = Tree()
        tree.add_node("root")
        tree.add_node("child1", parent="root")
        tree.add_node("child2", parent="root")
        tree.add_node("grandchild", parent="child1")
        print(tree.render())
    """

    def __init__(self, color: Optional[str] = None, branch_color: Optional[str] = "dim"):
        """Initialize a Tree.

        Args:
            color: Optional ANSI color name from COLORS dict for node labels.
            branch_color: ANSI color name for branch lines (default 'dim').
        """
        self.color = color
        self.branch_color = branch_color
        self._color_code = COLORS.get(color, "") if color else ""
        self._branch_code = COLORS.get(branch_color, COLORS["dim"]) if branch_color else ""
        self._nodes: Dict[str, Dict[str, Any]] = {}  # name -> {label, parent, children}
        self._roots: List[str] = []

    def add_node(self, label: str, parent: Optional[str] = None):
        """Add a node to the tree.

        Args:
            label: The display label for the node.
            parent: Optional parent node label. If None, this is a root node.
        """
        name = label  # Use label as node identifier
        if name in self._nodes:
            return  # Already exists

        self._nodes[name] = {"label": label, "parent": parent, "children": []}

        if parent and parent in self._nodes:
            self._nodes[parent]["children"].append(name)
        else:
            self._roots.append(name)

    def render(self) -> str:
        """Render the tree structure.

        Returns:
            A string containing the rendered tree.
        """
        if not self._nodes:
            return ""

        lines: List[str] = []
        reset = COLORS["reset"]
        bc = self._branch_code
        cc = self._color_code

        for i, root_name in enumerate(self._roots):
            is_last_root = (i == len(self._roots) - 1)
            self._render_node(root_name, "", is_last_root, lines, bc, cc, reset)

        return "\n".join(lines)

    def _render_node(
        self,
        name: str,
        prefix: str,
        is_last: bool,
        lines: List[str],
        bc: str,
        cc: str,
        reset: str,
    ):
        """Recursively render a node and its children."""
        node = self._nodes[name]
        connector = "└── " if is_last else "├── "
        line = f"{bc}{prefix}{connector}{reset}{cc}{node['label']}{reset}"
        lines.append(line)

        children = node["children"]
        for i, child_name in enumerate(children):
            child_is_last = (i == len(children) - 1)
            extension = "    " if is_last else "│   "
            self._render_node(child_name, prefix + extension, child_is_last, lines, bc, cc, reset)


class Divider:
    """Horizontal rule / divider with optional centered text.

    Example:
        div = Divider()
        print(div.render("Section 1"))
        print(div.render("", style="double"))
        print(div.render("END", style="bold"))
    """

    def __init__(self, width: int = 60, color: Optional[str] = "dim"):
        """Initialize a Divider.

        Args:
            width: Total width of the divider line.
            color: Optional ANSI color name from COLORS dict.
        """
        self.width = width
        self.color = color
        self._color_code = COLORS.get(color, "") if color else ""

    def render(self, text: str = "", style: str = "single") -> str:
        """Render the divider.

        Args:
            text: Optional text to display in the center of the divider.
            style: Divider character style: single, double, bold, dashed, dotted, ascii, heavy.

        Returns:
            A string containing the rendered divider.
        """
        reset = COLORS["reset"]
        cc = self._color_code
        char = DIVIDER_CHARS.get(style, DIVIDER_CHARS["single"])
        w = self.width

        if text:
            inner = f" {text} "
            if len(inner) >= w:
                return f"{cc}{inner}{reset}"
            left_len = (w - len(inner)) // 2
            right_len = w - len(inner) - left_len
            return f"{cc}{char * left_len}{reset}{text}{cc}{char * right_len}{reset}"
        else:
            return f"{cc}{char * w}{reset}"


# ══════════════════════════════════════════════════════════════════════════════
# Demonstration / Smoke Tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(COLORS["bold"] + "═══ Box Widget ═══" + COLORS["reset"])
    box = Box(border_style="rounded", color="cyan")
    print(box.render("Hello, World!\nThis is a multi-line\nbox example.", title=" Box Demo "))
    print()

    print(COLORS["bold"] + "═══ Box Styles ═══" + COLORS["reset"])
    for style in ["single", "double", "rounded", "bold", "dashed", "ascii"]:
        b = Box(border_style=style, color="bright_cyan")
        print(b.render(f"Style: {style}"), end="\n\n")

    print(COLORS["bold"] + "═══ Panel Widget ═══" + COLORS["reset"])
    panel = Panel(color="bright_green", width=50)
    print(panel.render(
        "Dashboard",
        "SEO Swarm is operational.\nAll 10 agents are online.\nCrawl queue: 150 pages pending.",
        footer="CPU: 12%  |  Memory: 256MB  |  Uptime: 3h 42m"
    ))
    print()

    print(COLORS["bold"] + "═══ Table Widget (Bordered) ═══" + COLORS["reset"])
    table = Table(border=True, color="bright_blue")
    table.set_headers(
        ["Agent", "Score", "Status", "Time"],
        alignments=["left", "center", "center", "right"]
    )
    table.add_row(["SEO Auditor", "92", "✓ Pass", "2.4s"])
    table.add_row(["Link Checker", "78", "⚠ Warn", "8.1s"])
    table.add_row(["Meta Analyzer", "95", "✓ Pass", "1.1s"])
    table.add_row(["Speed Tester", "65", "✗ Fail", "12.3s"])
    print(table.render())
    print()

    print(COLORS["bold"] + "═══ Table Widget (Borderless) ═══" + COLORS["reset"])
    t2 = Table(border=False, color="bright_yellow")
    t2.set_headers(["URL", "Title", "H1"], alignments=["left", "left", "left"])
    t2.add_row(["/about", "About Us", "Our Story"])
    t2.add_row(["/pricing", "Pricing Plans", "Choose Your Plan"])
    t2.add_row(["/contact", "Contact", "Get In Touch"])
    print(t2.render())
    print()

    print(COLORS["bold"] + "═══ Tree Widget ═══" + COLORS["reset"])
    tree = Tree(color="bright_cyan", branch_color="dim")
    tree.add_node("SEO Swarm")
    tree.add_node("Crawler", parent="SEO Swarm")
    tree.add_node("Analyzer", parent="SEO Swarm")
    tree.add_node("Reporter", parent="SEO Swarm")
    tree.add_node("On-Page SEO", parent="Analyzer")
    tree.add_node("Off-Page SEO", parent="Analyzer")
    tree.add_node("Meta Tags", parent="On-Page SEO")
    tree.add_node("Headings", parent="On-Page SEO")
    tree.add_node("PDF Report", parent="Reporter")
    tree.add_node("HTML Report", parent="Reporter")
    print(tree.render())
    print()

    print(COLORS["bold"] + "═══ Divider Widget ═══" + COLORS["reset"])
    div = Divider(width=50, color="dim")
    print(div.render("INTRODUCTION"))
    print("Some content here...")
    print(div.render("", style="dashed"))
    print("More content here...")
    print(div.render("CONCLUSION", style="double"))
    print()

    print(COLORS["bright_green"] + "All widget tests passed!" + COLORS["reset"])
