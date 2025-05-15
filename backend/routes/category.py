from flask import request, jsonify
from flask_jwt_extended import jwt_required
from backend import db
from backend.models.category import Category, CategorySchema
from backend.routes import category_bp
from backend.utils.decorators import admin_required

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

def validate_category_data(data, category=None):
    """Helper function to validate category data"""
    errors = {}
    
    if 'name' in data and (not category or data['name'] != category.name):
        if Category.query.filter_by(name=data['name']).first():
            errors['name'] = 'Category name already exists'
    
    if 'slug' in data and (not category or data['slug'] != category.slug):
        if Category.query.filter_by(slug=data['slug']).first():
            errors['slug'] = 'Slug already in use'
    
    return errors

@category_bp.route('/', methods=['GET'])
def get_categories():
    """Get all active parent categories"""
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    return jsonify({
        'success': True,
        'data': categories_schema.dump(categories)
    }), 200

@category_bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    """Get category details"""
    category = Category.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    }), 200

@category_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """Create new category (Admin only)"""
    data = request.get_json()
    
    # Validation
    if errors := validate_category_data(data):
        return jsonify({
            'success': False,
            'errors': errors
        }), 400
    
    # Create category
    category = Category(
        name=data['name'],
        slug=data.get('slug') or data['name'].lower().replace(' ', '-'),
        description=data.get('description'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    }), 201

@category_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(id):
    """Update category (Admin only)"""
    category = Category.query.get_or_404(id)
    data = request.get_json()
    
    # Validation
    if errors := validate_category_data(data, category):
        return jsonify({
            'success': False,
            'errors': errors
        }), 400
    
    # Update fields
    if 'name' in data:
        category.name = data['name']
    if 'slug' in data:
        category.slug = data['slug']
    if 'description' in data:
        category.description = data['description']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    if 'is_active' in data:
        category.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    }), 200

@category_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(id):
    """Soft delete category (Admin only)"""
    category = Category.query.get_or_404(id)
    category.is_active = False
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Category deactivated'
    }), 200