from core.models import ChangeKind
from core.semantic import diff_documents


def test_cambio_real_se_detecta():
    esperado = [("Cláusula Tercera.", 1)]
    actual = [("Cláusula Cuarta.", 1)]

    resultado = diff_documents(actual, esperado)

    assert not resultado.matches
    assert len(resultado.discrepancies) == 1
    cambios = resultado.discrepancies[0].internal_changes
    assert any(c.kind == ChangeKind.REAL for c in cambios)


def test_dato_variable_con_corchetes_se_distingue_de_cambio_real():
    esperado = [("Cliente: [ ].", 1)]
    actual = [("Cliente: Juan Pérez.", 1)]

    resultado = diff_documents(actual, esperado)

    cambios = resultado.discrepancies[0].internal_changes
    assert all(c.kind == ChangeKind.VARIABLE_FILL for c in cambios)
    assert any("Juan Pérez" in c.description for c in cambios)


def test_monto_con_guion_bajo_simple_se_detecta_sin_configuracion():
    esperado = [("El monto es $______ pesos.", 1)]
    actual = [("El monto es $100,000.00 pesos.", 1)]

    resultado = diff_documents(actual, esperado)

    cambios = resultado.discrepancies[0].internal_changes
    assert all(c.kind == ChangeKind.MONTO_FILL for c in cambios)


def test_monto_con_texto_de_formato_pegado_no_se_detecta_sin_tokens():
    # El espacio extra antes del ")" en el actual evita que "M.N." quede como
    # token idéntico en ambos lados, igual que pasa en documentos reales, así
    # que se agrupa junto con el monto en el mismo bloque de cambio.
    esperado = [("Monto: $______ (______________ / 100 M.N.).", 1)]
    actual = [("Monto: $100,000.00 (CIEN MIL PESOS 00/100 M.N. ).", 1)]

    resultado = diff_documents(actual, esperado)

    cambios = resultado.discrepancies[0].internal_changes
    # Sin decirle qué es "M.N.", el motor no asume nada y lo trata como cambio real.
    assert any(c.kind == ChangeKind.REAL for c in cambios)


def test_monto_con_texto_de_formato_se_detecta_con_monetary_noise_tokens():
    esperado = [("Monto: $______ (______________ / 100 M.N.).", 1)]
    actual = [("Monto: $100,000.00 (CIEN MIL PESOS 00/100 M.N. ).", 1)]

    resultado = diff_documents(actual, esperado, monetary_noise_tokens=["M.N.", "MN"])

    cambios = resultado.discrepancies[0].internal_changes
    assert all(c.kind == ChangeKind.MONTO_FILL for c in cambios)


def test_hide_variable_fills_oculta_rellenos_pero_no_cambios_reales():
    esperado = [("Cliente: [ ], monto $______.", 1)]
    actual = [("Cliente: Juan Pérez, monto $500.00.", 1)]

    resultado = diff_documents(actual, esperado, hide_variable_fills=True)

    # Todos los cambios eran rellenos (corchete + monto), así que el bloque
    # completo se descarta por no quedar ninguna discrepancia real.
    assert resultado.matches
    assert resultado.discrepancies == []


def test_texto_identico_no_genera_discrepancias():
    lineas = [("El texto es exactamente igual.", 1)]

    resultado = diff_documents(lineas, lineas)

    assert resultado.matches
    assert resultado.discrepancies == []
