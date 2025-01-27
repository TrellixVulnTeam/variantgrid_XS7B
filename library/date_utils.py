def get_month_and_year(run_date):
    run_date_str = "%d" % int(run_date)
    parts = [run_date_str[i:i + 2] for i in range(0, len(run_date_str), 2)]
    return int(parts[1]), int(parts[0])


def year_month_string(y, m):
    return "%02d%02d" % (y, m)


def date_to_month_year_string(d):
    return month_year_string(d.year, d.month)


def month_year_string(y, m):
    return "%02d/%02d" % (m, int(str(y)[2:]))


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def get_months_since(start_month, start_year, month, year):
    return (year - start_year) * 12 + month - start_month


def month_range(start_month, start_year, offset_start, offset_end, fmt=year_month_string):
    num_months = offset_end - offset_start
    labels = [fmt(start_year + (start_month + i) // 12, 1 + (start_month + i) % 12) for i in range(-1, num_months)]
    return labels
