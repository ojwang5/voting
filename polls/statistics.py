from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from django.db.models import Count

from .models import Election, Position, Vote


@dataclass(frozen=True)
class CandidateStat:
    candidate_id: int
    candidate_name: str
    position_name: str
    rank_display: str
    force_number: str
    votes: int
    percentage: float


def get_candidate_pie_stats(election: Election) -> Tuple[Dict[Position, List[CandidateStat]], int]:
    """Return aggregated candidate vote counts grouped by position."""
    total_votes = Vote.objects.filter(election=election).count()

    qs = (
        election.candidates.select_related("position")
        .annotate(votes=Count("vote"))
        .order_by("position__id", "name")
    )

    position_stats: Dict[Position, List[CandidateStat]] = OrderedDict()
    for c in qs:
        votes = int(c.votes)
        pos = c.position
        if pos not in position_stats:
            position_stats[pos] = []
        pct = (votes / total_votes * 100.0) if total_votes > 0 else 0.0
        position_stats[pos].append(
            CandidateStat(
                candidate_id=c.id,
                candidate_name=c.name,
                position_name=pos.name,
                rank_display=c.get_rank_display(),
                force_number=c.force_number,
                votes=votes,
                percentage=round(pct, 1),
            )
        )

    return position_stats, int(total_votes)


def render_candidate_pie_chart_png(stats: List[CandidateStat], *, size: int = 520) -> bytes:
    """Render a pie chart to PNG for a single position's candidates."""
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont

    slices = [(s.votes, s.candidate_name) for s in stats if s.votes > 0]

    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    pad = int(size * 0.08)
    bbox = (pad, pad, size - pad, size - pad)

    draw.ellipse(bbox, fill=(249, 250, 251, 255), outline=(226, 232, 240, 255), width=2)

    total = sum(v for v, _ in slices)
    if total <= 0:
        draw.ellipse(bbox, outline=(37, 99, 235, 120), width=6)
        return _png_bytes(img)

    palette = [
        (37, 99, 235, 255),
        (16, 185, 129, 255),
        (245, 158, 11, 255),
        (239, 68, 68, 255),
        (99, 102, 241, 255),
        (236, 72, 153, 255),
        (14, 116, 144, 255),
        (124, 58, 237, 255),
        (3, 105, 161, 255),
        (133, 77, 14, 255),
    ]

    start_angle = -90
    for idx, (votes, name) in enumerate(slices):
        end_angle = start_angle + (votes / total) * 360
        color = palette[idx % len(palette)]
        draw.pieslice(bbox, start_angle, end_angle, fill=color, outline=(255, 255, 255, 255), width=2)
        start_angle = end_angle

    try:
        font = ImageFont.truetype("arial.ttf", size=18)
    except Exception:
        font = ImageFont.load_default()

    max_legends = 8
    legend_slices = slices[:max_legends]
    if len(slices) > max_legends:
        others_votes = sum(v for v, _ in slices[max_legends:])
        legend_slices.append((others_votes, "Others"))

    legend_x = pad + 10
    legend_y = size - pad - 160
    legend_font = font
    box_size = 14
    for i, (votes, name) in enumerate(legend_slices):
        if votes <= 0:
            continue
        color = palette[i % len(palette)]
        y = legend_y + i * 18
        draw.rectangle([legend_x, y, legend_x + box_size, y + box_size], fill=color, outline=(255, 255, 255, 255))
        pct = (votes / total * 100.0) if total > 0 else 0.0
        label = name[:16]
        draw.text((legend_x + box_size + 8, y - 1), f"{label}: {pct:.0f}%", fill=(31, 41, 55, 255), font=legend_font)

    return _png_bytes(img)


def _png_bytes(img) -> bytes:
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
