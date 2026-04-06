"""
Views for Financial Records CRUD operations.

CRUD = Create, Read, Update, Delete
These are the core operations for managing financial data.

Access control:
- Viewers: Can only GET (read) records
- Analysts: Can only GET (read) records
- Admins: Can GET, POST, PUT, DELETE records
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import FinancialRecord
from .serializers import FinancialRecordSerializer, FinancialRecordListSerializer
from .filters import FinancialRecordFilter
from users.permissions import IsActiveUser, ReadOnlyForViewers


@api_view(['GET', 'POST'])
@permission_classes([IsActiveUser, ReadOnlyForViewers])
def record_list_create(request):
    """
    List all records (GET) or create a new record (POST).
    
    GET  /api/records/           - List records (all roles)
    POST /api/records/           - Create record (admin only)
    
    Query parameters for filtering:
    - transaction_type: income or expense
    - category: salary, food, etc.
    - date_from: YYYY-MM-DD
    - date_to: YYYY-MM-DD
    - amount_min: minimum amount
    - amount_max: maximum amount
    - search: search in descriptions
    - ordering: field to sort by (e.g., -date, amount)
    - page: page number for pagination
    """
    if request.method == 'GET':
        # Start with non-deleted records only
        queryset = FinancialRecord.objects.filter(is_deleted=False)
        
        # Apply filters
        filterset = FinancialRecordFilter(request.query_params, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        
        # Apply search in description
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(description__icontains=search)
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-date')
        allowed_orderings = ['date', '-date', 'amount', '-amount', 
                           'created_at', '-created_at', 'category', '-category']
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        
        # Manual pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        page_size = min(page_size, 100)  # Cap at 100 per page
        
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        records = queryset[start:end]
        serializer = FinancialRecordListSerializer(records, many=True)
        
        return Response({
            'success': True,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'data': serializer.data,
        })
    
    elif request.method == 'POST':
        serializer = FinancialRecordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Financial record created successfully.',
                'data': serializer.data,
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 400,
                'message': 'Failed to create record. Please check your input.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsActiveUser, ReadOnlyForViewers])
def record_detail(request, record_id):
    """
    Get, update, or delete a specific record.
    
    GET    /api/records/<id>/   - View record (all roles)
    PUT    /api/records/<id>/   - Update record (admin only)
    PATCH  /api/records/<id>/   - Partial update (admin only)
    DELETE /api/records/<id>/   - Soft-delete record (admin only)
    """
    try:
        record = FinancialRecord.objects.get(id=record_id, is_deleted=False)
    except FinancialRecord.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'Financial record with ID {record_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = FinancialRecordSerializer(record)
        return Response({
            'success': True,
            'data': serializer.data,
        })
    
    elif request.method in ('PUT', 'PATCH'):
        serializer = FinancialRecordSerializer(
            record,
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request},
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Financial record updated successfully.',
                'data': serializer.data,
            })
        
        return Response({
            'success': False,
            'error': {
                'code': 400,
                'message': 'Failed to update record. Please check your input.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Soft delete - mark as deleted, don't actually remove
        record.soft_delete()
        return Response({
            'success': True,
            'message': f'Financial record #{record_id} has been deleted.',
        }, status=status.HTTP_200_OK)
