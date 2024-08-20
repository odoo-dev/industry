# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.api import Environment, SUPERUSER_ID
from odoo.tools.translate import _lt

def _generate_construction_articles(env):
    user = env.user.with_context(lang="fr_FR") 
    render_ctx = {'object': user}
    body = env['ir.qweb']._render(
        'knowledge.knowledge_article_user_onboarding',
        render_ctx,
        minimal_qcontext=True,
        raise_if_not_found=False
    )
    if body:
        article_data = {
            'article_member_ids': [(0, 0, {
                'partner_id': user.partner_id.id,
                'permission': 'write',
            })],
            'body': _lt(body),
            'icon': "👋",
            'internal_permission': 'none',
            'is_article_visible_by_everyone': True,
            'favorite_ids': [(0, 0, {
                'sequence': 0,
                'user_id': user.id,
            })],
            'name': "welcome",
        }
        print(article_data)
        env['knowledge.article'].sudo().create(article_data)