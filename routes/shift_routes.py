from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from utils.db import get_db_connection
from utils.auth import login_required
from utils.rbac import require_permission

shift_bp = Blueprint('shift', __name__)

@shift_bp.route('/shifts')
@login_required
@require_permission('admin.settings')
def index():
    return render_template('manage_shifts.html')

@shift_bp.route('/api/shifts')
@login_required
@require_permission('admin.settings')
def get_shifts_api():
    try:
        conn = get_db_connection()
        shifts = conn.execute('SELECT * FROM shift_types ORDER BY name').fetchall()
        pass # conn.close() removed to prevent leak in Flask g
        
        shifts_list = [dict(row) for row in shifts]
        return jsonify({'success': True, 'shifts': shifts_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shift_bp.route('/api/shifts/add', methods=['POST'])
@login_required
@require_permission('admin.settings')
def add_shift_api():
    try:
        data = request.json
        name = data.get('name')
        start_time = data.get('start_time', '09:00')
        end_time = data.get('end_time', '17:00')
        hours_per_day = data.get('hours_per_day', 8)
        
        # Presence Window
        presence_start = data.get('presence_start_time')
        presence_end = data.get('presence_end_time')
        
        # If empty string, convert to None
        if not presence_start: presence_start = None
        if not presence_end: presence_end = None
        flex_mode = data.get('flex_mode') or 'none'
        if flex_mode not in ('none', 'any_time', 'fixed_hours'):
            flex_mode = 'none'
        
        if not name:
            return jsonify({'success': False, 'message': 'اسم الشفت مطلوب'})
            
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO shift_types (name, start_time, end_time, hours_per_day, presence_start_time, presence_end_time, flex_mode, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (name, start_time, end_time, hours_per_day, presence_start, presence_end, flex_mode))
            conn.commit()
            return jsonify({'success': True, 'message': 'تم إضافة الشفت بنجاح'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            pass # conn.close() removed to prevent leak in Flask g
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shift_bp.route('/api/shifts/update', methods=['POST'])
@login_required
@require_permission('admin.settings')
def update_shift_api():
    try:
        data = request.json
        shift_id = data.get('id')
        name = data.get('name')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        hours_per_day = data.get('hours_per_day')
        
        presence_start = data.get('presence_start_time')
        presence_end = data.get('presence_end_time')
        
        if not presence_start: presence_start = None
        if not presence_end: presence_end = None
        flex_mode = data.get('flex_mode') or 'none'
        if flex_mode not in ('none', 'any_time', 'fixed_hours'):
            flex_mode = 'none'
        
        if not shift_id or not name:
            return jsonify({'success': False, 'message': 'بيانات غير مكتملة'})
            
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE shift_types
                SET name=?, start_time=?, end_time=?, hours_per_day=?, presence_start_time=?, presence_end_time=?, flex_mode=?
                WHERE id=?
            ''', (name, start_time, end_time, hours_per_day, presence_start, presence_end, flex_mode, shift_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'تم تحديث الشفت بنجاح'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            pass # conn.close() removed to prevent leak in Flask g
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shift_bp.route('/api/shifts/delete/<int:id>', methods=['POST'])
@login_required
@require_permission('admin.settings')
def delete_shift_api(id):
    try:
        conn = get_db_connection()
        try:
            # Check usage in employees table
            count = conn.execute('SELECT COUNT(*) FROM employees WHERE shift_type = (SELECT name FROM shift_types WHERE id = ?)', (id,)).fetchone()[0]
            if count > 0:
                 return jsonify({'success': False, 'message': f'لا يمكن حذف هذا الشفت لأنه مستخدم من قبل {count} موظف'})
            
            conn.execute('DELETE FROM shift_types WHERE id = ?', (id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'تم حذف الشفت بنجاح'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            pass # conn.close() removed to prevent leak in Flask g
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
