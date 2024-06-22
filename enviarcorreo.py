from props import EmailSend

mensaje = """
    <h2>jajajajja</h2>
    <p>Las contraseñas de aplicación te ayudan a iniciar sesión en tu cuenta de Google en aplicaciones y servicios antiguos que no son compatibles con los estándares de seguridad modernos.</p>

<p>Las contraseñas de aplicación son menos seguras que usar aplicaciones y servicios actualizados que utilicen estándares de seguridad modernos. Antes de crear una contraseña de aplicación, debes comprobar si tu aplicación la necesita para iniciar sesión.</p>
"""

correo = EmailSend()
correo.send_email('prueba', str(mensaje))