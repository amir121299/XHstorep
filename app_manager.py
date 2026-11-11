import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid

DB_FILE = 'db.js'

# ================= توابع دیتابیس =================
def load_db():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, 'r', encoding='utf-8') as f: content = f.read()
    start_idx = content.find('[')
    end_idx = content.rfind(']') + 1
    if start_idx != -1 and end_idx != -1:
        try: return json.loads(content[start_idx:end_idx])
        except: return []
    return []

def save_db(data):
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    js_content = f"const appsData = {json_str};\n"
    with open(DB_FILE, 'w', encoding='utf-8') as f: f.write(js_content)

# ================= توابع رابط کاربری =================
def add_field(parent, label_text, is_text=False, height=4):
    ttk.Label(parent, text=label_text).pack(anchor="e", pady=(5,2), padx=10)
    widget = tk.Text(parent, height=height, font=('Arial', 10)) if is_text else ttk.Entry(parent, justify='right', font=('Arial', 10))
    widget.pack(fill=tk.X, padx=10, pady=2)
    return widget

def clear_form(fields):
    for key, widget in fields.items():
        if isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
        else:
            widget.delete(0, tk.END)

def get_data_from_fields(fields):
    return {
        "name": fields['name'].get(),
        "developer": fields['dev'].get(),
        "category": fields['cat'].get(),
        "badge": fields['badge'].get(),
        "size": fields['size'].get(),
        "shortDesc": fields['short_desc'].get(),
        "desc": fields['desc'].get("1.0", tk.END).strip(),
        "requirements": fields['reqs'].get("1.0", tk.END).strip(),
        "guide": fields['guide'].get("1.0", tk.END).strip(),
        "icon": fields['icon'].get(),
        "headerImage": fields['header'].get(),
        "video": fields['video'].get(),
        "screenshots": [s.strip() for s in fields['screenshots'].get("1.0", tk.END).strip().split('\n') if s.strip()],
        "link": fields['link'].get()
    }

def fill_form(fields, app_data):
    clear_form(fields)
    fields['name'].insert(0, app_data.get('name', ''))
    fields['dev'].insert(0, app_data.get('developer', ''))
    fields['cat'].insert(0, app_data.get('category', ''))
    fields['badge'].insert(0, app_data.get('badge', ''))
    fields['size'].insert(0, app_data.get('size', ''))
    fields['short_desc'].insert(0, app_data.get('shortDesc', ''))
    fields['icon'].insert(0, app_data.get('icon', ''))
    fields['header'].insert(0, app_data.get('headerImage', ''))
    fields['video'].insert(0, app_data.get('video', ''))
    fields['link'].insert(0, app_data.get('link', ''))
    
    fields['desc'].insert("1.0", app_data.get('desc', ''))
    fields['reqs'].insert("1.0", app_data.get('requirements', ''))
    fields['guide'].insert("1.0", app_data.get('guide', ''))
    fields['screenshots'].insert("1.0", '\n'.join(app_data.get('screenshots', [])))

# ================= منطق عملیات =================
def add_app(fields):
    data = get_data_from_fields(fields)
    if not data['name'] or not data['icon'] or not data['category']:
        messagebox.showerror("خطا", "نام، دسته‌بندی و آیکون اجباری است!")
        return
    data['id'] = str(uuid.uuid4())[:8]
    
    db_data = load_db()
    db_data.append(data)
    save_db(db_data)
    messagebox.showinfo("موفقیت", f"برنامه {data['name']} به استور اضافه شد!")
    clear_form(fields)
    refresh_list()

def refresh_list():
    for row in tree.get_children():
        tree.delete(row)
    for app in load_db():
        tree.insert("", "end", iid=app['id'], values=(app['name'], app['category'], app['id']))

def delete_app():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("توجه", "لطفاً ابتدا یک برنامه را از لیست انتخاب کنید.")
        return
    app_id = selected[0]
    
    confirm = messagebox.askyesno("تایید حذف", "آیا مطمئن هستید که می‌خواهید این برنامه را حذف کنید؟")
    if confirm:
        db_data = load_db()
        db_data = [app for app in db_data if app['id'] != app_id]
        save_db(db_data)
        refresh_list()
        messagebox.showinfo("حذف شد", "برنامه با موفقیت حذف شد.")

def open_edit_window():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("توجه", "لطفاً یک برنامه را برای ویرایش انتخاب کنید.")
        return
    app_id = selected[0]
    
    db_data = load_db()
    app_to_edit = next((app for app in db_data if app['id'] == app_id), None)
    
    if not app_to_edit: return

    # ساخت پنجره ویرایش
    edit_win = tk.Toplevel(root)
    edit_win.title(f"ویرایش: {app_to_edit['name']}")
    edit_win.geometry("600x750")
    
    nb = ttk.Notebook(edit_win)
    nb.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    t1, t2, t3 = ttk.Frame(nb), ttk.Frame(nb), ttk.Frame(nb)
    nb.add(t1, text='مشخصات'); nb.add(t2, text='راهنما'); nb.add(t3, text='رسانه')
    
    edit_fields = create_form_fields(t1, t2, t3)
    fill_form(edit_fields, app_to_edit)
    
    def save_edit():
        updated_data = get_data_from_fields(edit_fields)
        if not updated_data['name'] or not updated_data['icon'] or not updated_data['category']:
            messagebox.showerror("خطا", "نام، دسته‌بندی و آیکون اجباری است!")
            return
        updated_data['id'] = app_id # حفظ آیدی قبلی
        
        # جایگزینی در دیتابیس
        for i, app in enumerate(db_data):
            if app['id'] == app_id:
                db_data[i] = updated_data
                break
        
        save_db(db_data)
        messagebox.showinfo("موفقیت", "تغییرات با موفقیت ذخیره شد!")
        edit_win.destroy()
        refresh_list()

    tk.Button(edit_win, text="ذخیره تغییرات", font=('Arial', 14, 'bold'), bg="#3b82f6", fg="white", command=save_edit).pack(fill=tk.X, padx=20, pady=10, ipady=10)

def create_form_fields(t1, t2, t3):
    fields = {}
    fields['name'] = add_field(t1, "نام برنامه:")
    fields['dev'] = add_field(t1, "توسعه دهنده:")
    fields['cat'] = add_field(t1, "دسته بندی (مانند: برنامه، بازی):")
    row_frame = ttk.Frame(t1); row_frame.pack(fill=tk.X, pady=5)
    fields['badge'] = add_field(row_frame, "برچسب (اختیاری):")
    fields['size'] = add_field(row_frame, "حجم فایل:")
    fields['short_desc'] = add_field(t1, "توضیح کوتاه:")
    fields['desc'] = add_field(t1, "توضیحات کامل:", True, 5)
    
    fields['reqs'] = add_field(t2, "مشخصات سیستم / گوشی مورد نیاز:", True, 8)
    fields['guide'] = add_field(t2, "راهنمای نصب و استفاده:", True, 8)
    
    fields['icon'] = add_field(t3, "لینک آیکون (اجباری):")
    fields['header'] = add_field(t3, "لینک بنر بالای صفحه (اختیاری):")
    fields['video'] = add_field(t3, "لینک ویدیو تریلر MP4 (اختیاری):")
    ttk.Label(t3, text="لینک عکس‌های محیط برنامه (هر لینک در یک خط):").pack(anchor="e", pady=2, padx=10)
    fields['screenshots'] = tk.Text(t3, height=5, font=('Arial', 10))
    fields['screenshots'].pack(fill=tk.X, padx=10, pady=2)
    fields['link'] = add_field(t3, "لینک دانلود فایل اصلی:")
    return fields

# ================= رابط کاربری اصلی =================
root = tk.Tk()
root.title("XH Store - Manager Pro")
root.geometry("650x750")

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
style.configure("Treeview", font=('Arial', 10), rowheight=30)

tk.Label(root, text="مدیریت مارکت XH Store", font=('Arial', 16, 'bold'), fg="#3b82f6").pack(pady=10)

main_notebook = ttk.Notebook(root)
main_notebook.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

# ----- تب اول: افزودن برنامه -----
tab_add = ttk.Frame(main_notebook)
main_notebook.add(tab_add, text='➕ افزودن برنامه جدید')

add_nb = ttk.Notebook(tab_add)
add_nb.pack(fill=tk.BOTH, expand=True, pady=5)
t1, t2, t3 = ttk.Frame(add_nb), ttk.Frame(add_nb), ttk.Frame(add_nb)
add_nb.add(t1, text='مشخصات اصلی'); add_nb.add(t2, text='راهنما و سیستم'); add_nb.add(t3, text='لینک‌های رسانه')

add_fields = create_form_fields(t1, t2, t3)
tk.Button(tab_add, text="ثبت و درج در استور", font=('Arial', 14, 'bold'), bg="#10b981", fg="white", command=lambda: add_app(add_fields)).pack(fill=tk.X, padx=20, pady=15, ipady=10)

# ----- تب دوم: مدیریت (لیست، حذف، ویرایش) -----
tab_manage = ttk.Frame(main_notebook)
main_notebook.add(tab_manage, text='⚙️ مدیریت برنامه‌ها (حذف/ویرایش)')

columns = ('name', 'category', 'id')
tree = ttk.Treeview(tab_manage, columns=columns, show='headings')
tree.heading('name', text='نام برنامه')
tree.heading('category', text='دسته‌بندی')
tree.heading('id', text='آیدی (ID)')
tree.column('name', width=200, anchor='e')
tree.column('category', width=100, anchor='center')
tree.column('id', width=100, anchor='center')
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

btn_frame = ttk.Frame(tab_manage)
btn_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Button(btn_frame, text="🔄 بروزرسانی لیست", font=('Arial', 11), bg="#6b7280", fg="white", command=refresh_list).pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)
tk.Button(btn_frame, text="✏️ ویرایش برنامه", font=('Arial', 11, 'bold'), bg="#f59e0b", fg="white", command=open_edit_window).pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)
tk.Button(btn_frame, text="🗑️ حذف برنامه", font=('Arial', 11, 'bold'), bg="#ef4444", fg="white", command=delete_app).pack(side=tk.LEFT, padx=5, ipady=5, ipadx=10)

# بارگذاری اولیه لیست
refresh_list()

root.mainloop()