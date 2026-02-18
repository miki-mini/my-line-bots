from PIL import Image, ImageDraw, ImageFont
import calendar
import datetime
import os
import jpholiday
import PIL

def create_calendar(year, month, logo_path, output_path):
    print(f"--- Generating calendar for {year}-{month} ---")
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
        print(f"Error: Logo file not found at {os.path.abspath(logo_path)}")
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

        # Try to load font_month_name with size 40
        try:
            font_month_name = ImageFont.truetype("arial.ttf", 40)
        except IOError:
             font_month_name = ImageFont.load_default()

        font_days = ImageFont.truetype("arial.ttf", 30)
        font_dates = ImageFont.truetype("arial.ttf", 45) # Smaller dates
    except IOError as e:
        print(f"Warning: Font loading error ({e}). Using default font.")
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
    # Helper to get text size safely
    def get_text_size(text, font):
        if hasattr(draw, 'textbbox'):
             bbox = draw.textbbox((0, 0), text, font=font)
             return bbox[2] - bbox[0]
        else:
             return draw.textsize(text, font=font)[0]

    year_width = get_text_size(year_text, font_sub_header)
    month_width = get_text_size(month_name, font_month_name)
    num_width = get_text_size(month_num_text, font_sub_header)

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
        text_w = get_text_size(day, font_days)
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
                text_w = get_text_size(day_str, font_dates)

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

    abs_path = os.path.abspath(output_path)
    img.save(abs_path)
    print(f"Saved calendar to: {abs_path}")

if __name__ == "__main__":
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Pillow Version: {PIL.__version__}")

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
    print("All tasks completed.")
