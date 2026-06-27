"""
SEO SWARM - Responsive Terminal Layout Engine
==============================================
Pure ANSI escape code layout engine with zero external dependencies.
Provides grid layouts, column layouts, flex rows, and a persistent status bar.
"""

import shutil
import re
import textwrap
from typing import List, Optional, Tuple


# ── ANSI helpers ────────────────────────────────────────────────────────────

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string for width calculation."""
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _visible_width(text: str) -> int:
    """Calculate visible width of a string, ignoring ANSI codes."""
    return len(_strip_ansi(text))


def _pad_to_width(text: str, width: int, align: str = 'left') -> str:
    """Pad a string to a given visible width, handling ANSI codes."""
    visible = _visible_width(text)
    if visible >= width:
        return text
    padding = width - visible
    if align == 'right':
        return ' ' * padding + text
    elif align == 'center':
        left = padding // 2
        right = padding - left
        return ' ' * left + text + ' ' * right
    else:  # left
        return text + ' ' * padding


def _wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to a given width, preserving ANSI codes across lines."""
    if width <= 0:
        return []
    clean = _strip_ansi(text)
    if len(clean) <= width:
        return [text]

    # For simplicity, wrap by words while preserving ANSI formatting
    ansi_prefix = ''
    ansi_match = re.match(r'^(\033\[[0-9;]*m)', text)
    if ansi_match:
        ansi_prefix = ansi_match.group(1)

    lines = []
    wrapped = textwrap.wrap(clean, width=width)
    for line in wrapped:
        if ansi_prefix:
            lines.append(ansi_prefix + line + '\033[0m')
        else:
            lines.append(line)
    return lines


def _truncate_text(text: str, width: int, suffix: str = '…') -> str:
    """Truncate text to fit within width, preserving ANSI codes."""
    ansi_prefix = ''
    ansi_match = re.match(r'^(\033\[[0-9;]*m)', text)
    if ansi_match:
        ansi_prefix = ansi_match.group(1)

    clean = _strip_ansi(text)
    if len(clean) <= width:
        return text
    truncated = clean[:max(0, width - len(suffix))] + suffix
    if ansi_prefix:
        return ansi_prefix + truncated + '\033[0m'
    return truncated


# ═══════════════════════════════════════════════════════════════════════════════
# LAYOUT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class Layout:
    """Responsive grid layout for terminal.

    Usage:
        layout = Layout(columns=2)
        layout.add_pane("Hello", row=0, col=0)
        layout.add_pane("World", row=0, col=1)
        print(layout.render())
    """

    def __init__(self, columns: int = 1, gap: int = 1):
        self.columns = columns
        self.gap = gap  # spaces between columns
        self._panes: List[dict] = []
        self._grid: dict = {}  # (row, col) -> pane index

    def add_pane(
        self,
        content: str,
        row: int = 0,
        col: int = 0,
        row_span: int = 1,
        col_span: int = 1,
        wrap: bool = True,
        align: str = 'left',
        border: bool = False,
        title: str = '',
    ):
        """Add a content pane to the grid layout.

        Args:
            content: String content for the pane (may include ANSI codes).
            row: Starting row index (0-based).
            col: Starting column index (0-based).
            row_span: Number of rows this pane spans.
            col_span: Number of columns this pane spans.
            wrap: If True, wrap content; if False, truncate.
            align: Text alignment: 'left', 'center', 'right'.
            border: If True, draw a border around the pane.
            title: Optional title displayed at top of border.
        """
        idx = len(self._panes)
        self._panes.append({
            'content': content,
            'row': row,
            'col': col,
            'row_span': row_span,
            'col_span': col_span,
            'wrap': wrap,
            'align': align,
            'border': border,
            'title': title,
        })
        # Mark grid occupancy
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                self._grid[(r, c)] = idx
        return self

    def render(self, terminal_width: Optional[int] = None) -> str:
        """Render the grid layout to a string.

        Args:
            terminal_width: Override terminal width (auto-detected if None).
        """
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size((80, 24)).columns

        if not self._panes:
            return ''

        # Determine grid dimensions
        max_row = max((p['row'] + p['row_span']) for p in self._panes)
        actual_cols = min(self.columns, terminal_width)

        # Calculate column widths
        total_gap = self.gap * (actual_cols - 1)
        col_width = (terminal_width - total_gap) // actual_cols
        extra = (terminal_width - total_gap) % actual_cols

        col_widths = [col_width] * actual_cols
        for i in range(extra):
            col_widths[i] += 1

        # Build row-by-row
        rows_output = []
        for r in range(max_row):
            row_content = self._render_row(r, col_widths, actual_cols, total_gap)
            rows_output.append(row_content)

        return '\n'.join(rows_output)

    def _render_row(self, row_idx: int, col_widths: List[int],
                    actual_cols: int, total_gap: int) -> str:
        """Render a single row of the grid."""
        parts = []
        for c in range(actual_cols):
            pane_info = self._get_pane_at(row_idx, c)
            width = col_widths[c]

            if pane_info is None:
                parts.append(' ' * width)
            else:
                pane = self._panes[pane_info]
                # Only render if this is the top-left corner of the pane
                if pane['row'] == row_idx and pane['col'] == c:
                    # Calculate total width for this pane (across columns)
                    total_w = 0
                    for cc in range(c, min(c + pane['col_span'], actual_cols)):
                        total_w += col_widths[cc]
                        if cc < min(c + pane['col_span'], actual_cols) - 1:
                            total_w += self.gap

                    rendered = self._render_pane(pane, total_w)
                    parts.append(rendered)
                else:
                    # Part of a multi-column/multi-row pane already rendered
                    parts.append('')

        # Join with gaps, handling multi-column panes
        result = []
        skip_until = -1
        for c in range(actual_cols):
            if c < skip_until:
                continue
            pane_info = self._get_pane_at(row_idx, c)
            if pane_info is not None:
                pane = self._panes[pane_info]
                if pane['row'] == row_idx and pane['col'] == c:
                    total_w = 0
                    for cc in range(c, min(c + pane['col_span'], actual_cols)):
                        total_w += col_widths[cc]
                        if cc < min(c + pane['col_span'], actual_cols) - 1:
                            total_w += self.gap
                    rendered = self._render_pane(pane, total_w)
                    result.append(rendered)
                    skip_until = c + pane['col_span']
                else:
                    continue
            else:
                result.append(' ' * col_widths[c])
                skip_until = c + 1

        # Join with gap spaces
        gap_str = ' ' * self.gap
        return gap_str.join(result)

    def _get_pane_at(self, row: int, col: int) -> Optional[int]:
        """Get the pane index occupying a grid cell."""
        return self._grid.get((row, col), None)

    def _render_pane(self, pane: dict, width: int) -> str:
        """Render a single pane to fit within given width."""
        content = pane['content']
        if not content:
            return ' ' * width

        inner_width = width
        if pane['border']:
            inner_width = max(1, width - 4)  # borders + padding

        if pane['wrap']:
            lines = _wrap_text(content, inner_width)
        else:
            lines = [_truncate_text(content, inner_width)]

        # Align each line
        aligned_lines = []
        for line in lines:
            if pane['align'] == 'right':
                aligned_lines.append(_pad_to_width(line, inner_width, 'right'))
            elif pane['align'] == 'center':
                aligned_lines.append(_pad_to_width(line, inner_width, 'center'))
            else:
                aligned_lines.append(_pad_to_width(line, inner_width, 'left'))

        if pane['border']:
            return self._add_border(aligned_lines, width, pane.get('title', ''))
        else:
            return '\n'.join(aligned_lines)

    @staticmethod
    def _add_border(lines: List[str], width: int, title: str = '') -> str:
        """Wrap content in a box-drawing border."""
        top = '┌' + '─' * (width - 2) + '┐'
        if title:
            title_text = ' ' + _truncate_text(title, width - 4) + ' '
            top = '┌' + title_text.ljust(width - 2, '─')[:width - 2] + '┐'
        bottom = '└' + '─' * (width - 2) + '┘'
        bordered = [top]
        for line in lines:
            padded = _pad_to_width(line, width - 4 if width >= 4 else 0)
            bordered.append('│ ' + padded + ' │')
        bordered.append(bottom)
        return '\n'.join(bordered)


class Columns:
    """Side-by-side column layout with configurable width ratios.

    Usage:
        cols = Columns(widths=[0.5, 0.3, 0.2])
        cols.add_column("Left panel content")
        cols.add_column("Center content")
        cols.add_column("Right sidebar")
        print(cols.render())
    """

    def __init__(self, widths: Optional[List[float]] = None, gap: int = 2):
        self.widths = widths or []  # ratios, e.g. [0.5, 0.3, 0.2]
        self.gap = gap
        self._columns: List[str] = []
        self._wrap_enabled: List[bool] = []

    def add_column(self, content: str, wrap: bool = True):
        """Add a column of content."""
        self._columns.append(content)
        self._wrap_enabled.append(wrap)

    def render(self, terminal_width: Optional[int] = None) -> str:
        """Render columns side-by-side as a string."""
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size((80, 24)).columns

        num_cols = len(self._columns)
        if num_cols == 0:
            return ''

        # Determine column widths
        if self.widths and len(self.widths) >= num_cols:
            ratios = self.widths[:num_cols]
            # Normalize ratios
            total_ratio = sum(ratios) or 1.0
            ratios = [r / total_ratio for r in ratios]
        else:
            # Equal widths
            ratios = [1.0 / num_cols] * num_cols

        total_gap = self.gap * (num_cols - 1)
        available = terminal_width - total_gap

        col_widths = []
        for r in ratios:
            cw = max(1, int(available * r))
            col_widths.append(cw)

        # Adjust for rounding errors
        diff = available - sum(col_widths)
        for i in range(diff):
            if i < len(col_widths):
                col_widths[i] += 1

        # Wrap each column
        wrapped_columns = []
        max_lines = 0
        for i, content in enumerate(self._columns):
            if self._wrap_enabled[i]:
                lines = _wrap_text(content, col_widths[i])
            else:
                lines = [_truncate_text(content, col_widths[i])]
            wrapped_columns.append(lines)
            max_lines = max(max_lines, len(lines))

        # Pad all columns to max_lines
        for i in range(num_cols):
            while len(wrapped_columns[i]) < max_lines:
                wrapped_columns[i].append(' ' * col_widths[i])

        # Build rows
        gap_str = ' ' * self.gap
        rows = []
        for line_idx in range(max_lines):
            row_parts = []
            for col_idx in range(num_cols):
                line = wrapped_columns[col_idx][line_idx]
                row_parts.append(_pad_to_width(line, col_widths[col_idx]))
            rows.append(gap_str.join(row_parts))

        return '\n'.join(rows)


class FlexRow:
    """Horizontal row with flexible items.

    Usage:
        row = FlexRow()
        row.add("Short", flex=1, min_width=10)
        row.add("A much longer piece of content", flex=2, min_width=20)
        print(row.render())
    """

    def __init__(self, gap: int = 2):
        self.gap = gap
        self._items: List[dict] = []

    def add(self, content: str, flex: int = 1, min_width: int = 10,
            align: str = 'left', truncate: bool = True):
        """Add a flexible item to the row.

        Args:
            content: String content.
            flex: Flex weight (higher = more space).
            min_width: Minimum width in characters.
            align: 'left', 'center', 'right'.
            truncate: If True, truncate overflowing content.
        """
        self._items.append({
            'content': content,
            'flex': flex,
            'min_width': min_width,
            'align': align,
            'truncate': truncate,
        })

    def render(self, terminal_width: Optional[int] = None) -> str:
        """Render the flex row as a single line."""
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size((80, 24)).columns

        if not self._items:
            return ''

        total_flex = sum(item['flex'] for item in self._items)
        total_min = sum(item['min_width'] for item in self._items)
        total_gap = self.gap * (len(self._items) - 1)

        available = terminal_width - total_gap - total_min
        if available < 0:
            available = 0

        # Distribute extra space by flex weight
        parts = []
        for item in self._items:
            extra = int(available * (item['flex'] / total_flex)) if total_flex > 0 else 0
            item_width = item['min_width'] + extra

            if item['truncate']:
                rendered = _truncate_text(item['content'], item_width)
            else:
                rendered = item['content'][:item_width]

            if item['align'] == 'right':
                rendered = _pad_to_width(rendered, item_width, 'right')
            elif item['align'] == 'center':
                rendered = _pad_to_width(rendered, item_width, 'center')
            else:
                rendered = _pad_to_width(rendered, item_width, 'left')

            parts.append(rendered)

        gap_str = ' ' * self.gap
        return gap_str.join(parts)


class StatusBar:
    """Persistent bottom status bar with left, center, and right sections.

    Usage:
        sb = StatusBar()
        sb.set_left("SEO SWARM v1.0.0")
        sb.set_center("Ready")
        sb.set_right("Memory: 1.2MB")
        print(sb.render())
    """

    # Box-drawing characters
    _EDGE_LEFT = '├'
    _EDGE_RIGHT = '┤'
    _SEP = '│'

    def __init__(self, theme_color: str = '\033[90m'):
        self._left = ''
        self._center = ''
        self._right = ''
        self._theme_color = theme_color  # dim/bright black for status bar
        self._reset = '\033[0m'

    def set_left(self, text: str):
        """Set the left section text."""
        self._left = text

    def set_center(self, text: str):
        """Set the center section text."""
        self._center = text

    def set_right(self, text: str):
        """Set the right section text."""
        self._right = text

    def render(self, width: Optional[int] = None) -> str:
        """Render the status bar.

        Format: ├─ LEFT ──────│────── CENTER ──────│────── RIGHT ─┤
        """
        if width is None:
            width = shutil.get_terminal_size((80, 24)).columns

        # Available space for text (accounting for edges and separators)
        inner_width = max(1, width - 2)  # two edge chars

        # Calculate section widths
        sep_count = 2  # number of separators
        section_width = inner_width // 3
        extra = inner_width % 3

        left_w = section_width + (1 if extra > 0 else 0)
        center_w = section_width + (1 if extra > 1 else 0)
        right_w = section_width

        # Truncate and pad each section
        left_text = _truncate_text(self._left, left_w)
        center_text = _truncate_text(self._center, center_w)
        right_text = _truncate_text(self._right, right_w)

        left_padded = _pad_to_width(left_text, left_w, 'left')
        center_padded = _pad_to_width(center_text, center_w, 'center')
        right_padded = _pad_to_width(right_text, right_w, 'right')

        # Build bar
        c = self._theme_color
        r = self._reset
        bar = (
            f'{c}{self._EDGE_LEFT}{r} '
            f'{left_padded}'
            f'{c} {self._SEP} {r}'
            f'{center_padded}'
            f'{c} {self._SEP} {r}'
            f'{right_padded}'
            f' {c}{self._EDGE_RIGHT}{r}'
        )
        return bar


# ═══════════════════════════════════════════════════════════════════════════════
# COMMON HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def render_table(
    headers: List[str],
    rows: List[List[str]],
    col_widths: Optional[List[int]] = None,
    border: bool = True,
) -> str:
    """Render a simple bordered table.

    Args:
        headers: Column header strings.
        rows: List of row data (each row is a list of strings).
        col_widths: Optional forced column widths.
        border: Whether to draw borders.
    """
    num_cols = len(headers)
    all_data = [headers] + rows if headers else rows

    # Calculate column widths
    if col_widths is None:
        col_widths = [len(str(h)) for h in headers] if headers else [0] * num_cols
        for row in rows:
            for i, cell in enumerate(row[:num_cols]):
                col_widths[i] = max(col_widths[i], _visible_width(str(cell)))
        col_widths = [w + 2 for w in col_widths]  # padding

    total_width = sum(col_widths) + num_cols + 1  # separators + right border

    def _format_row(items: List[str]) -> str:
        parts = []
        for i, item in enumerate(items):
            if i < len(col_widths):
                parts.append(f' {_pad_to_width(str(item), col_widths[i] - 2)} ')
        return '│' + '│'.join(parts) + '│'

    lines = []
    if border:
        lines.append('┌' + '┬'.join('─' * w for w in col_widths) + '┐')
        if headers:
            lines.append(_format_row(headers))
            lines.append('├' + '┼'.join('─' * w for w in col_widths) + '┤')
        for row in rows:
            lines.append(_format_row(row))
        lines.append('└' + '┴'.join('─' * w for w in col_widths) + '┘')
    else:
        if headers:
            lines.append('  '.join(headers))
        for row in rows:
            lines.append('  '.join(str(c) for c in row))

    return '\n'.join(lines)


def render_bar(value: float, max_value: float = 100.0, width: int = 20,
               filled_char: str = '█', empty_char: str = '░',
               color: str = '', label: str = '') -> str:
    """Render a single-bar progress/score indicator.

    Args:
        value: Current value.
        max_value: Maximum value.
        width: Bar width in characters.
        filled_char: Character for filled portion.
        empty_char: Character for empty portion.
        color: ANSI color code.
        label: Optional label before the bar.
    """
    ratio = max(0.0, min(1.0, value / max_value if max_value > 0 else 0))
    filled = int(ratio * width)
    empty = width - filled
    reset = '\033[0m'

    bar = f'{color}{filled_char * filled}{reset}{empty_char * empty}'
    pct = f'{ratio * 100:.0f}%'

    if label:
        return f'{label} {bar} {pct}'
    return f'{bar} {pct}'


def render_spinner(frame: int) -> str:
    """Return a single spinner frame character.

    Args:
        frame: Frame index (0-9) for 10-frame spinner.
    """
    spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    return spinners[frame % len(spinners)]
