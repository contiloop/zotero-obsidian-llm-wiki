{% bq %}
[!quote]{% if zt.pageLabel %} p.{{ zt.pageLabel }}{% endif %} [Zotero]({{ zt.backlink }})

{{ zt.imgLink | embed }}{{ zt.text }}
{% if zt.comment %}

**Note:** {{ zt.comment }}
{% endif %}
{% endbq %}
