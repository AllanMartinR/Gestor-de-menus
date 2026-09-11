from django.db import models
from django.core.validators import MinValueValidator
 
# Create your models here. 
 
# ---------------------------------------------------------------------------
# GERENTE REGIONAL
# ---------------------------------------------------------------------------
class GerenteRegional(models.Model):
    id_gerente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=150, unique=True)
 
    class Meta:
        db_table = "gerente_regional"
        verbose_name = "Gerente regional"
        verbose_name_plural = "Gerentes regionales"
 
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
 
# ---------------------------------------------------------------------------
# SUCURSAL
# ---------------------------------------------------------------------------
class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=150, blank=True)
 
    # Relación "supervisa": un gerente regional supervisa muchas sucursales
    gerente = models.ForeignKey(
        GerenteRegional,
        on_delete=models.PROTECT,
        related_name="sucursales",
        verbose_name="Gerente regional",
    )
 
    class Meta:
        db_table = "sucursal"
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
 
    def __str__(self):
        return self.nombre
 
# ---------------------------------------------------------------------------
# EMPLEADO
# ---------------------------------------------------------------------------
class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    puesto = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=150, unique=True)
    fecha_ingreso = models.DateField()
 
    # Relación "emplea": una sucursal emplea a muchos empleados
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="empleados",
    )
 
    class Meta:
        db_table = "empleado"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
 
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
 
# ---------------------------------------------------------------------------
# CLIENTE
# ---------------------------------------------------------------------------
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=150, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
 
    # Relación "atiende": una sucursal atiende a muchos clientes
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="clientes",
    )
 
    class Meta:
        db_table = "cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
 
    def __str__(self):
        return self.nombre
 
# ---------------------------------------------------------------------------
# PROVEEDOR
# ---------------------------------------------------------------------------
class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(max_length=150, blank=True)
 
    class Meta:
        db_table = "proveedor"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
 
    def __str__(self):
        return self.nombre
 
# ---------------------------------------------------------------------------
# INGREDIENTE
# ---------------------------------------------------------------------------
class Ingrediente(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('l', 'Litros'),
        ('pza', 'Piezas'),
    ]

    id_ingrediente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    unidad_medida = models.CharField(max_length=5, choices=UNIDADES)
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    activo = models.BooleanField(default=True)
 
    # Relación "suministra": un proveedor suministra muchos ingredientes
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="ingredientes",
    )
 
    class Meta:
        db_table = "ingrediente"
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ["nombre"]
 
    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()})"
 
# ---------------------------------------------------------------------------
# PLATILLO
# ---------------------------------------------------------------------------
class Platillo(models.Model):
    id_platillo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
 
    # Relación "requiere": un platillo requiere muchos ingredientes y viceversa
    ingredientes = models.ManyToManyField(
        Ingrediente,
        through="PlatilloIngrediente",
        related_name="platillos",
    )
 
    class Meta:
        db_table = "platillo"
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"
        ordering = ["nombre"]
 
    def __str__(self):
        return self.nombre
 
    def calcular_costo_total(self):
        """Suma cantidad * costo_unitario de cada ingrediente requerido."""
        total = sum(
            pi.cantidad * pi.ingrediente.costo_unitario
            for pi in self.platilloingrediente_set.select_related("ingrediente")
        )
        return total
 
# ---------------------------------------------------------------------------
# REQUIERE (tabla asociativa Platillo <-> Ingrediente)
# ---------------------------------------------------------------------------
class PlatilloIngrediente(models.Model):
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    unidad_medida = models.CharField(max_length=20)
 
    class Meta:
        db_table = "platillo_ingrediente"
        verbose_name = "Ingrediente del platillo"
        verbose_name_plural = "Ingredientes del platillo"
        unique_together = ("platillo", "ingrediente")
 
    def __str__(self):
        return f"{self.platillo} requiere {self.cantidad} {self.unidad_medida} de {self.ingrediente}"
 
# ---------------------------------------------------------------------------
# MENU
# ---------------------------------------------------------------------------
class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    numero_comensales = models.PositiveIntegerField(default=1)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_por_comensal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
 
    # Relación "incluye": un menú incluye muchos platillos y viceversa
    platillos = models.ManyToManyField(
        Platillo,
        through="MenuPlatillo",
        related_name="menus",
    )
 
    # Relación "solicita": clientes solicitan menús (con costo_total por solicitud)
    clientes = models.ManyToManyField(
        Cliente,
        through="Solicitud",
        related_name="menus_solicitados",
    )
 
    class Meta:
        db_table = "menu"
        verbose_name = "Men\u00fa"
        verbose_name_plural = "Men\u00fas"
        ordering = ["nombre"]
 
    def __str__(self):
        return self.nombre
 
    def recalcular_costos(self, guardar=True):
        """Recalcula costo_total (suma de platillos incluidos) y costo_por_comensal."""
        total = sum(
            mp.platillo.costo_total for mp in self.menuplatillo_set.select_related("platillo")
        )
        self.costo_total = total
        self.costo_por_comensal = (
            total / self.numero_comensales if self.numero_comensales else 0
        )
        if guardar:
            self.save(update_fields=["costo_total", "costo_por_comensal"])
        return self.costo_total, self.costo_por_comensal
 
# ---------------------------------------------------------------------------
# INCLUYE (tabla asociativa Menu <-> Platillo)
# ---------------------------------------------------------------------------
class MenuPlatillo(models.Model):
    DIAS_SEMANA = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Mi\u00e9rcoles"),
        ("JUE", "Jueves"),
        ("VIE", "Viernes"),
        ("SAB", "S\u00e1bado"),
        ("DOM", "Domingo"),
    ]
 
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DIAS_SEMANA)
 
    class Meta:
        db_table = "menu_platillo"
        verbose_name = "Platillo del men\u00fa"
        verbose_name_plural = "Platillos del men\u00fa"
        unique_together = ("menu", "platillo", "dia_semana")
 
    def __str__(self):
        return f"{self.menu} - {self.platillo} ({self.get_dia_semana_display()})"
 
# ---------------------------------------------------------------------------
# SOLICITA (tabla asociativa Cliente <-> Menu)
# ---------------------------------------------------------------------------
class Solicitud(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="solicitudes"
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="solicitudes"
    )
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = "solicitud"
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
 
    def __str__(self):
        return f"{self.cliente} -> {self.menu} (${self.costo_total})"