from PIL import Image, ImageDraw, ImageFont
import calendar
import datetime
import os
import jpholiday

def create_calendar(year, month, logo_path, output_path):
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (30, 30, 30) # Softer black
    PYTHON_BLUE = (48, 105, 152)
    PYTHON_YELLOW = (255, 212, 59)
    RED = (200, 50, 50)
    GRAY = (150, 150, 150)

    # Size
    width = 1080
    height = 1920
    img = Image.new('RGB', (width, height), WHITE)
    draw = ImageDraw.Draw(img)

    # Load Logo
    if not os.path.exists(logo_path):
        print(f"Error: Logo file not found at {logo_path}")
        return

    try:
        logo = Image.open(logo_path)
        # Resize logo - smaller for a cooler look
        logo_width = int(width * 0.4)
        aspect_ratio = logo.height / logo.width
        logo_height = int(logo_width * aspect_ratio)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Paste logo - nice vertical position
        logo_x = (width - logo_width) // 2
        logo_y = 200
        img.paste(logo, (logo_x, logo_y), logo if logo.mode == 'RGBA' else None)
    except Exception as e:
        print(f"Error loading logo: {e}")
        return

    # Fonts
    try:
        # Smaller, cleaner fonts
        font_header = ImageFont.truetype("arial.ttf", 60) # Smaller header
        font_sub_header = ImageFont.truetype("arial.ttf", 30) # Year
        font_month_name = ImageFont.truetype("arial.ttf", 40) # Slightly larger month name
        font_days = ImageFont.truetype("arial.ttf", 30)
        font_dates = ImageFont.truetype("arial.ttf", 45) # Smaller dates
    except IOError:
        print("Warning: arial.ttf not found, using default font.")
        font_header = ImageFont.load_default()
        font_sub_header = ImageFont.load_default()
        font_month_name = ImageFont.load_default()
        font_days = ImageFont.load_default()
        font_dates = ImageFont.load_default()

    # Draw Header Information
    year_text = f"{year}"
    month_name = calendar.month_name[month].upper()
    month_num_text = f"{month}"

    # Calculate text sizes
    if hasattr(draw, 'textbbox'):
        # Year
        bbox_year = draw.textbbox((0, 0), year_text, font=font_sub_header)
        year_width = bbox_year[2] - bbox_year[0]
        # Month Name
        bbox_month = draw.textbbox((0, 0), month_name, font=font_month_name)
        month_width = bbox_month[2] - bbox_month[0]
        # Month Number
        bbox_num = draw.textbbox((0, 0), month_num_text, font=font_sub_header)
        num_width = bbox_num[2] - bbox_num[0]
    else:
        year_width, _ = draw.textsize(year_text, font=font_sub_header)
        month_width, _ = draw.textsize(month_name, font=font_month_name)
        num_width, _ = draw.textsize(month_num_text, font=font_sub_header)

    # Position text
    current_y = logo_y + logo_height + 50
    spacing = 50 # Spacing between lines

    # 1. Year (Top)
    draw.text(((width - year_width) // 2, current_y), year_text, fill=GRAY, font=font_sub_header)
    current_y += spacing

    # 2. Month Name (Middle)
    draw.text(((width - month_width) // 2, current_y), month_name, fill=BLACK, font=font_month_name)
    current_y += spacing

    # 3. Month Number (Bottom)
    draw.text(((width - num_width) // 2, current_y), month_num_text, fill=GRAY, font=font_sub_header)

    # Draw Days
    cal_obj = calendar.Calendar(firstweekday=6)
    week_days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    start_y = current_y + 150
    col_width = width // 7

    # Draw Headers
    for i, day in enumerate(week_days):
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), day, font=font_days)
            text_w = bbox[2] - bbox[0]
        else:
            text_w, _ = draw.textsize(day, font=font_days)

        x = i * col_width + (col_width - text_w) // 2

        color = GRAY
        if i == 0: color = RED
        if i == 6: color = PYTHON_BLUE

        draw.text((x, start_y), day, fill=color, font=font_days)

    # Draw Grid
    month_days = cal_obj.monthdayscalendar(year, month)
    row_height = 120 # More compact rows
    current_y = start_y + 100

    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                day_str = str(day)
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0, 0), day_str, font=font_dates)
                    text_w = bbox[2] - bbox[0]
                else:
                    text_w, _ = draw.textsize(day_str, font=font_dates)

                x = i * col_width + (col_width - text_w) // 2

                # Determine color
                color = BLACK
                is_holiday = jpholiday.is_holiday(datetime.date(year, month, day))

                if i == 0 or is_holiday: # Sunday or Holiday
                    color = RED
                elif i == 6: # Saturday
                    color = PYTHON_BLUE

                draw.text((x, current_y), day_str, fill=color, font=font_dates)
        current_y += row_height

    img.save(output_path)
    print(f"Saved calendar to {output_path}")

if __name__ == "__main__":
    today = datetime.date.today()
    # Generate for current month
    create_calendar(today.year, today.month, "images/python-logo-only.png", f"python_calendar_{today.year}_{today.month:02d}.png")

    # Generate for next month
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

    create_calendar(next_year, next_month, "images/python-logo-only.png", f"python_calendar_{next_year}_{next_month:02d}.png")
