from app.extensions import db,ma
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.userId'))
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True)
    variants = db.relationship('ProductVariant', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    name = db.Column(db.String(100), nullable=False)  # e.g., "Color", "Size"
    value = db.Column(db.String(100), nullable=False)  # e.g., "Red", "XL"
    additional_price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True

class ProductImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImage
        load_instance = True

class ProductVariantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductVariant
        load_instance = True