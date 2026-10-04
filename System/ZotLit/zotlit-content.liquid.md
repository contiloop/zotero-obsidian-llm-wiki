{%- if zt.notes.size > 0 %}
## Notes

{% for note in zt.notes -%}
- {{ note.noteLink }}
{% endfor %}
{% endif -%}
{%- if zt.annotations.size > 0 %}
## Highlights
{%- assign groups = "yellow|Key claims,red|Data & figures,green|For my writing,blue|Definitions & concepts,purple|Counterpoints & questions,orange|Outlook & forecasts" | split: "," -%}
{%- for g in groups -%}
{%- assign parts = g | split: "|" -%}
{%- assign list = zt.annotations | where: "colorName", parts[0] -%}
{%- if list.size > 0 %}

### {{ parts[1] }} ({{ parts[0] }})
{%- for annotation in list %}

{% render "annotation" with annotation as zt %}
{%- endfor -%}
{%- endif -%}
{%- endfor -%}
{%- capture others -%}
{%- for annotation in zt.annotations -%}
{%- unless "yellow,red,green,blue,purple,orange" contains annotation.colorName %}

{% render "annotation" with annotation as zt %}
{%- endunless -%}
{%- endfor -%}
{%- endcapture -%}
{%- assign others_trimmed = others | strip -%}
{%- if others_trimmed != "" %}

### Other colors
{{- others -}}
{%- endif %}
{% endif -%}
