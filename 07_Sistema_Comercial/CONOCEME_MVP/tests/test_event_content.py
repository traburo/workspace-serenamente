def test_landing_contains_confirmed_event_data(client):
    content = client.get("/conoceme").get_data(as_text=True)
    assert "1 de octubre de 2026" in content
    assert "Sede Pedro Fontova" in content
    assert "$30.000" in content
    assert "máximo 20 duplas" in content


def test_serenamente_brand_links_to_official_site(client):
    content = client.get("/conoceme").get_data(as_text=True)
    assert 'href="https://serenamente-landing-page-seven.vercel.app/#top"' in content
    assert 'aria-label="Ir al sitio oficial de Serenamente"' in content
