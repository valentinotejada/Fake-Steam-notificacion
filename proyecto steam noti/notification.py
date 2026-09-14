
COLORES_PRUEBA = [
    "#101820",
]

import tkinter as tk


# =========================================================
# CONFIGURACIÓN
# =========================================================

ANCHO = 300
ALTO = 90

TIEMPO_ENTRADA = 600
TIEMPO_VISIBLE = 5000
TIEMPO_SALIDA = 600

MAX_NOTIFICACIONES = 3

SEPARACION = 0
DELAY_SALIDA = 10

PASOS_ANIMACION = 60


# =========================================================
# SISTEMA
# =========================================================

notificaciones = []

cola_salida = []
cola_espera = []

# Notificaciones que esperan a que termine la entrada
# de la anterior.
cola_entrada = []

procesando_salida = False

contador_notificaciones = 0

root = None


# =========================================================
# LIMPIADOR DE NOTIFICACIONES
# =========================================================

def limpiar_cola_notificaciones():

    cola_entrada.clear()
    cola_espera.clear()


# Indica que actualmente hay una notificación entrando.
entrada_en_curso = False


# =========================================================
# POSICIÓN QUE DEBE TENER UNA NOTIFICACIÓN
# =========================================================

def obtener_posicion(noti):

    indice = notificaciones.index(noti)

    total = len(notificaciones)

    # La más nueva queda abajo.
    posicion_desde_abajo = total - 1 - indice

    return (
        noti["alto_pantalla"]
        - ALTO
        - posicion_desde_abajo * (ALTO + SEPARACION)
    )


# =========================================================
# ANIMAR EMPUJE
# =========================================================

def animar_empuje():

    movimientos = []

    for noti in notificaciones:

        if not noti["saliendo"]:
            ventana = noti["ventana"]

            if not ventana.winfo_exists():
                continue

            y_inicial = noti["y"]
            y_final = obtener_posicion(noti)

            # Si ya está en su lugar, no necesitamos animarla.
            if int(y_inicial) == int(y_final):
                continue

            movimientos.append(
                (noti, y_inicial, y_final)
            )

    if not movimientos:
        return

    posicion = 0

    def animar():

        nonlocal posicion

        posicion += 1

        progreso = posicion / PASOS_ANIMACION

        for noti, y_inicial, y_final in movimientos:

            if not noti["ventana"].winfo_exists():
                continue

            y = (
                y_inicial
                + (y_final - y_inicial)
                * progreso
            )

            noti["y"] = y

            nueva_y = int(y)

            if noti["ventana"].winfo_y() != nueva_y:
                noti["ventana"].geometry(
                    f"{ANCHO}x{ALTO}+"
                    f"{noti['x']}+{nueva_y}"
                )

        if posicion < PASOS_ANIMACION:

            root.after(
                TIEMPO_ENTRADA // PASOS_ANIMACION,
                animar
            )

        else:

            for noti, _, y_final in movimientos:

                noti["y"] = y_final

                if noti["ventana"].winfo_exists():

                    noti["ventana"].geometry(
                        f"{ANCHO}x{ALTO}+"
                        f"{noti['x']}+{int(y_final)}"
                    )

    animar()


# =========================================================
# COMPROBAR SI HAY UNA ENTRADA EN CURSO
# =========================================================

def hay_entrada_en_curso():

    for noti in notificaciones:

        if noti["entrando"]:

            return True

    return False


# =========================================================
# PROCESAR COLA DE ENTRADAS
# =========================================================

def procesar_cola_entrada():

    if not cola_entrada:
        return

    # Si todavía hay una entrando, esperamos.
    if hay_entrada_en_curso():
        return

    # Sacar UNA sola.
    cola_entrada.pop(0)

    mostrar_notificacion()


# =========================================================
# MOSTRAR NOTIFICACIÓN
# =========================================================

def mostrar_notificacion():

    global contador_notificaciones
    global root

    # =====================================================
    # ESPERAR A QUE TERMINE LA ANTERIOR
    # =====================================================

    if hay_entrada_en_curso():

        cola_entrada.append(True)

        return

    # =====================================================
    # LÍMITE DE 6
    # =====================================================

    if len(notificaciones) >= MAX_NOTIFICACIONES:

        cola_espera.append(True)

        return

    # =====================================================
    # CONTADOR
    # =====================================================

    contador_notificaciones += 1

    numero = contador_notificaciones

    color = COLORES_PRUEBA[
        (numero - 1) % len(COLORES_PRUEBA)
    ]

    # =====================================================
    # CREAR VENTANA
    # =====================================================

    ventana = tk.Toplevel()

    if root is None:
        root = ventana.master

    ventana.overrideredirect(True)
    ventana.attributes("-topmost", True)

    ventana.configure(
        bg="#101820",
        bd=0,
        borderwidth=0,
        highlightthickness=0
    )

    # =====================================================
    # PANTALLA
    # =====================================================

    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    x = ancho_pantalla - ANCHO

    # =====================================================
    # TEXTO
    # =====================================================

    texto = tk.Label(
        ventana,
        text=f"🔔 NOTIFICACIÓN #{numero}",
        bg=color,
        fg="white",
        font=("Arial", 16)
    )

    texto.pack(expand=True)

    # =====================================================
    # DATOS
    # =====================================================

    noti = {
        "ventana": ventana,
        "numero": numero,

        "x": x,

        "y": alto_pantalla,

        "alto_pantalla": alto_pantalla,

        "saliendo": False,

        "salida_solicitada": False,

        # Esta notificación está entrando.
        "entrando": True
    }

    # =====================================================
    # AGREGAR AL FINAL
    #
    # La más nueva siempre queda ABAJO.
    # =====================================================

    notificaciones.append(noti)

    # =====================================================
    # POSICIÓN FINAL
    # =====================================================

    y_final_nueva = obtener_posicion(noti)

    # =====================================================
    # PREPARAR EMPUJE
    #
    # AHORA las anteriores ya terminaron de entrar.
    # Por eso podemos animarlas sin que otra animación
    # esté intentando moverlas al mismo tiempo.
    # =====================================================

    movimientos_antiguos = []

    for otra in notificaciones:

        if otra is not noti and not otra["saliendo"]:

            movimientos_antiguos.append(
                (
                    otra,
                    otra["y"],
                    obtener_posicion(otra)
                )
            )

    # =====================================================
    # ANIMACIÓN DE ENTRADA + EMPUJE
    # =====================================================

    pasos = PASOS_ANIMACION

    posicion_actual = 0

    y_inicial_nueva = alto_pantalla



    def entrar_y_empujar():

        nonlocal posicion_actual

        if not ventana.winfo_exists():
            return

        posicion_actual += 1

        progreso = posicion_actual / pasos

        # =================================================
        # NUEVA NOTIFICACIÓN
        # =================================================

        y_nueva = (
            y_inicial_nueva
            + (
                y_final_nueva
                - y_inicial_nueva
            ) * progreso
        )

        noti["y"] = y_nueva

        ventana.geometry(
            f"{ANCHO}x{ALTO}+"
            f"{x}+{int(y_nueva)}"
        )

        # =================================================
        # NOTIFICACIONES ANTERIORES
        #
        # Todas se mueven simultáneamente.
        # =================================================

        movimientos_frame = []

        for otra, y_inicial, y_final in movimientos_antiguos:

            if otra["saliendo"]:
                continue

            if not otra["ventana"].winfo_exists():
                continue

            y = (
                y_inicial
                + (
                    y_final
                    - y_inicial
                ) * progreso
            )

            otra["y"] = y

            movimientos_frame.append(
                (
                    otra,
                    int(y)
                )
            )

        for otra, y_redondeado in movimientos_frame:

            otra["ventana"].geometry(
                f"{ANCHO}x{ALTO}+"
                f"{otra['x']}+{y_redondeado}"
            )

        # =================================================
        # CONTINUAR
        # =================================================

        if posicion_actual < pasos:

            root.after(
                TIEMPO_ENTRADA // pasos,
                entrar_y_empujar
            )

        else:

            # -------------------------------------------------
            # POSICIONES EXACTAS
            # -------------------------------------------------

            noti["y"] = y_final_nueva

            noti["entrando"] = False

            ventana.geometry(
                f"{ANCHO}x{ALTO}+"
                f"{x}+{int(y_final_nueva)}"
            )

            for otra, _, y_final in movimientos_antiguos:

                if otra["saliendo"]:
                    continue

                otra["y"] = y_final

                if otra["ventana"].winfo_exists():

                    otra["ventana"].geometry(
                        f"{ANCHO}x{ALTO}+"
                        f"{otra['x']}+{int(y_final)}"
                    )

            # =================================================
            # SU TIEMPO VISIBLE
            # =================================================

            root.after(
                TIEMPO_VISIBLE,
                solicitar_salida
            )

            # =================================================
            # SI HAY OTRA ESPERANDO ENTRAR
            #
            # Esperamos un poquito y recién entonces
            # dejamos entrar a la siguiente.
            # =================================================

            if cola_entrada:

                root.after(
                    DELAY_SALIDA,
                    procesar_cola_entrada
                )

    # =====================================================
    # SOLICITAR SALIDA
    # =====================================================

    def solicitar_salida():

        if not ventana.winfo_exists():
            return

        if not noti["salida_solicitada"]:

            noti["salida_solicitada"] = True

            cola_salida.append(noti)

        procesar_salidas()

    # =====================================================
    # POSICIÓN INICIAL
    # =====================================================

    ventana.geometry(
        f"{ANCHO}x{ALTO}+"
        f"{x}+{alto_pantalla}"
    )

    # =====================================================
    # INICIAR
    # =====================================================

    root.after(
        100,
        entrar_y_empujar
    )


# =========================================================
# PROCESAR SALIDAS
# =========================================================

def procesar_salidas():

    global procesando_salida

    if procesando_salida:
        return

    if not cola_salida:
        return

    # -----------------------------------------------------
    # MÁS VIEJA PRIMERO
    # -----------------------------------------------------

    cola_salida.sort(
        key=lambda n: notificaciones.index(n)
    )

    noti = cola_salida.pop(0)

    procesando_salida = True

    iniciar_salida(noti)


# =========================================================
# ANIMACIÓN DE SALIDA
# =========================================================

def iniciar_salida(noti):

    ventana = noti["ventana"]

    if not ventana.winfo_exists():

        finalizar_salida(noti)

        return

    noti["saliendo"] = True

    pasos = PASOS_ANIMACION

    posicion_actual = 0

    y_inicial = noti["y"]

    y_final = noti["alto_pantalla"]

    def salir():

        nonlocal posicion_actual

        if not ventana.winfo_exists():

            finalizar_salida(noti)

            return

        posicion_actual += 1

        progreso = posicion_actual / pasos

        y = (
            y_inicial
            + (
                y_final
                - y_inicial
            ) * progreso
        )

        noti["y"] = y

        ventana.geometry(
            f"{ANCHO}x{ALTO}+"
            f"{noti['x']}+{int(y)}"
        )

        if posicion_actual < pasos:

            ventana.after(
                TIEMPO_SALIDA // pasos,
                salir
            )

        else:

            finalizar_salida(noti)

    salir()


# =========================================================
# FINALIZAR SALIDA
# =========================================================

def finalizar_salida(noti):

    global procesando_salida

    ventana = noti["ventana"]

    # -----------------------------------------------------
    # DESTRUIR
    # -----------------------------------------------------

    if ventana.winfo_exists():

        ventana.destroy()

    # -----------------------------------------------------
    # ELIMINAR
    # -----------------------------------------------------

    if noti in notificaciones:

        notificaciones.remove(noti)

    # -----------------------------------------------------
    # REUBICAR LAS RESTANTES
    # -----------------------------------------------------

    actualizar_posiciones_instantaneo()

    # -----------------------------------------------------
    # LIBERAR SALIDA
    # -----------------------------------------------------

    procesando_salida = False

    # -----------------------------------------------------
    # SIGUIENTE SALIDA
    # -----------------------------------------------------

    if cola_salida:

        root.after(
            DELAY_SALIDA,
            procesar_salidas
        )

        return

    # -----------------------------------------------------
    # SIGUIENTE DE LA COLA DE 6
    # -----------------------------------------------------

    if cola_espera:

        cola_espera.pop(0)

        root.after(
            DELAY_SALIDA,
            mostrar_notificacion
        )


# =========================================================
# REUBICAR DESPUÉS DE UNA SALIDA
# =========================================================

def actualizar_posiciones_instantaneo():

    if hay_entrada_en_curso():
        return

    for noti in notificaciones:

        if not noti["saliendo"] and not noti["entrando"]:

            nuevo_y = obtener_posicion(noti)

            noti["y"] = nuevo_y

            if noti["ventana"].winfo_exists():

                noti["ventana"].geometry(
                    f"{ANCHO}x{ALTO}+"
                    f"{noti['x']}+{int(nuevo_y)}"
                )
