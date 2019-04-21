from flask import render_template, request


def object_list(template_name, query, pagination_by=20, **kwargs):
    page = request.args.get('page', 1, type=int)
    object_list = query.pagination(page, pagination_by, False)
    return render_template(template_name, object_list=object_list, **kwargs)
