from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.product import Product, ProductImage, ProductVariant
from app.models.product import ProductSchema, ProductImageSchema, ProductVariantSchema
from app.utils.decorators import admin_required, seller_required, validate_schema
from . import api

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_image_schema = ProductImageSchema()
product_variant_schema = ProductVariantSchema()

@api.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    products = Product.query.filter_by(is_active=True).paginate(page=page, per_page=per_page)
    return jsonify({
        'products': products_schema.dump(products.items),
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    }), 200

@api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product), 200

@api.route('/products', methods=['POST'])
@jwt_required()
@seller_required
@validate_schema(product_schema)
def create_product():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        discount_price=data.get('discount_price'),
        category_id=data.get('category_id'),
        seller_id=current_user,
        stock=data.get('stock', 0),
        sku=data.get('sku')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return product_schema.jsonify(product), 201

@api.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
@seller_required
@validate_schema(product_schema)
def update_product(id):
    current_user = get_jwt_identity()
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user:
        return jsonify({'message': 'You can only update your own products'}), 403
    
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.discount_price = data.get('discount_price', product.discount_price)
    product.category_id = data.get('category_id', product.category_id)
    product.stock = data.get('stock', product.stock)
    product.sku = data.get('sku', product.sku)
    
    db.session.commit()
    return product_schema.jsonify(product), 200

@api.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
@seller_required
def delete_product(id):
    current_user = get_jwt_identity()
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user:
        return jsonify({'message': 'You can only delete your own products'}), 403
    
    product.is_active = False
    db.session.commit()
    return jsonify({'message': 'Product deactivated'}), 200

@api.route('/products/<int:id>/images', methods=['POST'])
@jwt_required()
@seller_required
def add_product_image(id):
    current_user = get_jwt_identity()
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user:
        return jsonify({'message': 'You can only add images to your own products'}), 403
    
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400
    
    image_file = request.files['image']
    image_url = upload_image_to_cloudinary(image_file)
    
    image = ProductImage(
        product_id=product.id,
        image_url=image_url,
        is_primary=request.form.get('is_primary', False)
    )
    
    db.session.add(image)
    db.session.commit()
    return product_image_schema.jsonify(image), 201

@api.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query
    products_query = Product.query.filter(Product.is_active == True)
    
    # Apply search term
    if query:
        products_query = products_query.filter(
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%')
            )
        )
    
    # Apply filters
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    if min_price:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price:
        products_query = products_query.filter(Product.price <= max_price)
    
    # Pagination
    products = products_query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'products': products_schema.dump(products.items),
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    }), 200