
def _generate_construction_articles(env):
    user = env.user
    render_ctx = {'object': user}
    body = env['ir.qweb']._render(
        'construction.construction_knowledge',
        render_ctx,
        raise_if_not_found=False,
    )
    if body:
        article_data = {
            'article_member_ids': [(0, 0, {
                'partner_id': user.partner_id.id,
                'permission': 'write',
            })],
            'body': body,
            'icon': "👷‍♂️",
            "cover_image_position" : 81.79,
            'internal_permission': 'none',
            'is_article_visible_by_everyone': True,
            'name': "Construction",
        }
        print(user.partner_id.id)
        article_record = env.ref('construction.knowledge_article_35')
        if article_record:
            article_record.sudo().write(article_data)
            
