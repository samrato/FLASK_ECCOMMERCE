from backend.extensions import db, ma
from datetime import datetime
from sqlalchemy.orm import validates

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')

    @validates('name')
    def validate_name(self, key, name):
        if not name.strip():
            raise ValueError("Category name cannot be empty")
        return name.strip()

    @validates('slug')
    def validate_slug(self, key, slug):
        if not slug.replace('-', '').isalnum():
            raise ValueError("Slug can only contain alphanumeric characters and hyphens")
        return slug.lower()

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        include_fk = True
        exclude = ('created_at', 'updated_at')  # Exclude these from serialization

    # Custom field for nested children
    children = ma.Nested('self', many=True, exclude=('children', 'parent'))
    parent = ma.Nested('self', exclude=('children', 'parent'))