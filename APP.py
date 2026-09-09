import streamlit as st
import math

# 网页页面基础配置
st.set_page_config(
    page_title="复合材料拉挤型材计算程序 (T/CECS 692-2020)",
    layout="wide"
)

st.title("🏗️ 复合材料拉挤型材计算程序 (T/CECS 692-2020)")
st.markdown("---")

# ================= 全局基础常量定义（必须在最上方） =================
SUPPORT_FACTOR = {"两端铰接": 1.0, "一端固定一端铰接": 0.8, "两端固定": 0.65, "一端固定一端自由": 2.0}

MAT_TABLE_DEF = {
    "M40级": {"f_L_t": 600, "f_T_t": 70, "E_L_t": 42000, "E_T_t": 7000, "f_L_c": 400, "f_T_c": 90, "E_L_c": 42000, "E_T_c": 7000, "f_sh": 28, "f_LT": 45, "G_LT": 2750},
    "M30级": {"f_L_t": 400, "f_T_t": 45, "E_L_t": 30000, "E_T_t": 7000, "f_L_c": 300, "f_T_c": 70, "E_L_c": 25000, "E_T_c": 7000, "f_sh": 28, "f_LT": 45, "G_LT": 2750},
    "M23级": {"f_L_t": 300, "f_T_t": 55, "E_L_t": 23000, "E_T_t": 7000, "f_L_c": 250, "f_T_c": 70, "E_L_c": 20000, "E_T_c": 7000, "f_sh": 25, "f_LT": 45, "G_LT": 2750},
    "M17级": {"f_L_t": 200, "f_T_t": 45, "E_L_t": 17000, "E_T_t": 5000, "f_L_c": 200, "f_T_c": 70, "E_L_c": 15000, "E_T_c": 5000, "f_sh": 20, "f_LT": 45, "G_LT": 2750}
}

# ================= 网页端与原代码的桥梁适配器 =================
class MockWidget:
    def __init__(self, val):
        self.val = str(val)
    def get(self):
        return self.val

class MockCombobox:
    def __init__(self, val):
        self.val = str(val)
    def get(self):
        return self.val

class MockBooleanVar:
    def __init__(self, val):
        self.val = bool(val)
    def get(self):
        return self.val

class MockTextOut:
    def __init__(self):
        self.content = []
    def insert(self, pos, text):
        self.content.append(text)
    def get_result(self):
        return "".join(self.content)

# ================= 侧边栏：参数控制面板 =================
st.sidebar.header("🎛️ 参数控制面板")

project_options = [
    "5.1 轴心受拉构件计算", 
    "5.2 轴心受压构件计算", 
    "6.1 受弯构件计算(含挠度)", 
    "6.1 受剪构件计算", 
    "6.1 受扭构件计算", 
    "6.5 集中荷载计算", 
    "6.6 拉弯构件组合验算 (6.6.1)", 
    "6.7 压弯构件组合验算 (6.6.2)", 
    "6.8 闭口弯扭轴组合验算 (6.6.3)", 
    "7.1 连接节点设计 (螺栓连接)", 
    "7.2 连接节点设计 (粘结连接)", 
    "7.3 连接节点设计 (胶栓混合连接)", 
    "8.2 组合梁受弯承载力计算 (待开发)"
]
project_sel = st.sidebar.selectbox("选择计算项目", project_options, index=2)

st.sidebar.subheader("1. 材料与环境设置")
fiber_sel = st.sidebar.selectbox("纤维类型", ["玻璃纤维(GFRP)", "碳纤维(CFRP)", "玄武岩纤维(BFRP)"])
grade_sel = st.sidebar.selectbox("型材等级", list(MAT_TABLE_DEF.keys()), index=1)
env_sel = st.sidebar.selectbox("服役环境", ["室内环境", "一般室外环境", "侵蚀/浸水/海洋环境"])
tg_val = st.sidebar.number_input("玻璃化温度 Tg (℃)", value=80.0)
tmax_val = st.sidebar.number_input("最高平均温度 Tmax (℃)", value=40.0)

default_mat = MAT_TABLE_DEF[grade_sel]
mat_vals_input = {}
with st.sidebar.expander("材料力学性能标准值 (规范表 3.3.5)", expanded=False):
    mat_vals_input["f_L_t"] = st.number_input("纵向拉伸强度 f_L^t", value=float(default_mat["f_L_t"]))
    mat_vals_input["f_T_t"] = st.number_input("横向拉伸强度 f_T^t", value=float(default_mat["f_T_t"]))
    mat_vals_input["E_L_t"] = st.number_input("纵向拉伸弹模 E_L^t", value=float(default_mat["E_L_t"]))
    mat_vals_input["E_T_t"] = st.number_input("横向拉伸弹模 E_T^t", value=float(default_mat["E_T_t"]))
    mat_vals_input["f_L_c"] = st.number_input("纵向压缩强度 f_L^c", value=float(default_mat["f_L_c"]))
    mat_vals_input["f_T_c"] = st.number_input("横向压缩强度 f_T^c", value=float(default_mat["f_T_c"]))
    mat_vals_input["E_L_c"] = st.number_input("纵向压缩弹模 E_L^c", value=float(default_mat["E_L_c"]))
    mat_vals_input["E_T_c"] = st.number_input("横向压缩弹模 E_T^c", value=float(default_mat["E_T_c"]))
    mat_vals_input["f_sh"] = st.number_input("层间剪切强度 f_sh", value=float(default_mat["f_sh"]))
    mat_vals_input["f_LT"] = st.number_input("面内剪切强度 f_LT", value=float(default_mat["f_LT"]))
    mat_vals_input["G_LT"] = st.number_input("面内剪切模量 G_LT", value=float(default_mat["G_LT"]))

st.sidebar.subheader("2. 截面与特征参数")
section_sel = st.sidebar.selectbox("截面类型", ["矩形管", "圆管", "双槽形", "槽形", "角形", "工字形", "T形", "实心截面"])
sub_sel = ""
if section_sel == "实心截面":
    sub_sel = st.sidebar.selectbox("实心形状", ["矩形实心", "正方形实心", "圆形实心"])

dim_vals_input = {}
if section_sel == "矩形管":
    dim_vals_input["高度尺寸 h (mm):"] = st.sidebar.number_input("高度尺寸 h (mm)", value=100.0)
    dim_vals_input["宽度尺寸 b (mm):"] = st.sidebar.number_input("宽度尺寸 b (mm)", value=50.0)
    dim_vals_input["高度壁厚 t1 (mm):"] = st.sidebar.number_input("高度壁厚 t1 (mm)", value=4.8)
    dim_vals_input["宽度壁厚 t2 (mm):"] = st.sidebar.number_input("宽度壁厚 t2 (mm)", value=4.8)
elif section_sel == "圆管":
    dim_vals_input["外径 D (mm):"] = st.sidebar.number_input("外径 D (mm)", value=60.0)
    dim_vals_input["壁厚 t (mm):"] = st.sidebar.number_input("壁厚 t (mm)", value=4.8)
elif section_sel == "双槽形":
    dim_vals_input["总高度 h (mm):"] = st.sidebar.number_input("总高度 h (mm)", value=100.0)
    dim_vals_input["总宽度 b (mm):"] = st.sidebar.number_input("总宽度 b (mm)", value=80.0)
    dim_vals_input["单翼缘宽度 bf (mm):"] = st.sidebar.number_input("单翼缘宽度 bf (mm)", value=30.0)
    dim_vals_input["腹板厚 tw (mm):"] = st.sidebar.number_input("腹板厚 tw (mm)", value=6.4)
    dim_vals_input["翼缘厚 tf (mm):"] = st.sidebar.number_input("翼缘厚 tf (mm)", value=6.4)
elif section_sel in ["槽形", "工字形"]:
    dim_vals_input["高度 h (mm):"] = st.sidebar.number_input("高度 h (mm)", value=100.0)
    dim_vals_input["宽度 b (mm):"] = st.sidebar.number_input("宽度 b (mm)", value=50.0)
    dim_vals_input["腹板厚 tw (mm):"] = st.sidebar.number_input("腹板厚 tw (mm)", value=6.4)
    dim_vals_input["翼缘厚 tf (mm):"] = st.sidebar.number_input("翼缘厚 tf (mm)", value=6.4)
elif section_sel == "角形":
    dim_vals_input["高度/肢1 h (mm):"] = st.sidebar.number_input("高度/肢1 h (mm)", value=80.0)
    dim_vals_input["宽度/肢2 b (mm):"] = st.sidebar.number_input("宽度/肢2 b (mm)", value=80.0)
    dim_vals_input["厚度 t (mm):"] = st.sidebar.number_input("厚度 t (mm)", value=6.4)
elif section_sel == "T形":
    dim_vals_input["总高度 h (mm):"] = st.sidebar.number_input("总高度 h (mm)", value=100.0)
    dim_vals_input["翼缘宽度 b (mm):"] = st.sidebar.number_input("翼缘宽度 b (mm)", value=100.0)
    dim_vals_input["腹板厚 tw (mm):"] = st.sidebar.number_input("腹板厚 tw (mm)", value=8.0)
    dim_vals_input["翼缘厚 tf (mm):"] = st.sidebar.number_input("翼缘厚 tf (mm)", value=8.0)
elif section_sel == "实心截面":
    if sub_sel == "矩形实心":
        dim_vals_input["高度 h (mm):"] = st.sidebar.number_input("高度 h (mm)", value=50.0)
        dim_vals_input["宽度 b (mm):"] = st.sidebar.number_input("宽度 b (mm)", value=40.0)
    elif sub_sel == "正方形实心":
        dim_vals_input["边长 a (mm):"] = st.sidebar.number_input("边长 a (mm)", value=50.0)
    elif sub_sel == "圆形实心":
        dim_vals_input["直径 d (mm):"] = st.sidebar.number_input("直径 d (mm)", value=50.0)

length_val = st.sidebar.number_input("构件总长度 L (mm)", value=2500.0)
support_sel = st.sidebar.selectbox("两端支座条件", list(SUPPORT_FACTOR.keys()))

st.sidebar.subheader("3. 专项与荷载设置")
is_known_load_val = st.sidebar.checkbox("已知荷载设计值", value=True)
load_val = st.sidebar.number_input("荷载设计值 (N/M/V/T/F)", value=30.0, disabled=not is_known_load_val)

extra_vals = {}
if "5.1" in project_sel:
    extra_vals["hole_type"] = st.sidebar.selectbox("开孔排布方式", ["无削弱", "平齐排列开孔", "锯齿/对角线排列开孔"])
    if extra_vals["hole_type"] != "无削弱":
        extra_vals["d_bolt"] = st.sidebar.number_input("螺栓公称直径 d (mm)", value=12.0)
        extra_vals["n_hole"] = st.sidebar.number_input("破坏面上同排孔数 n", value=2, step=1)
        extra_vals["t_plate"] = st.sidebar.number_input("开孔所在板厚 t (mm)", value=4.8)
elif "6.1" in project_sel and "受弯" in project_sel:
    extra_vals["bend_axis"] = st.sidebar.selectbox("弯曲主轴方向", ["绕强轴弯曲 (主轴 x-x)", "绕弱轴弯曲 (次轴 y-y)"])
    extra_vals["l_b"] = st.sidebar.number_input("侧向无支撑长度 Lb (mm)", value=2500.0)
    extra_vals["beta_b"] = st.sidebar.number_input("等效弯矩系数 βb", value=1.0)
    extra_vals["fv"] = st.sidebar.number_input("竖向荷载标准值 Fv (N)", value=5000.0)
    extra_vals["load_cond"] = st.sidebar.selectbox("荷载类型与边界条件", [
        "梁端简支, 满布均布荷载", "梁端简支, 跨中集中荷载", "悬臂端承受集中荷载", "悬臂端承受均布荷载", "梁端固结, 满布均布荷载"
    ])
elif "6.5" in project_sel:
    extra_vals["conc_type"] = st.sidebar.selectbox("集中荷载类型", ["集中受压荷载 (6.5.2)", "集中受拉荷载 (6.5.1)"])
    extra_vals["leff"] = st.sidebar.number_input("荷载分布长度 leff (mm)", value=100.0)
elif "6.6" in project_sel or "6.7" in project_sel or "6.8" in project_sel:
    extra_vals["mx"] = st.sidebar.number_input("强轴弯矩设计值 Mx (kN·m)", value=20.0)
    extra_vals["my"] = st.sidebar.number_input("弱轴弯矩设计值 My (kN·m)", value=5.0)
elif "7.1" in project_sel:
    extra_vals["bolt_case"] = st.sidebar.selectbox("受力工况状态", ["受拉，单排螺栓", "受拉，多排螺栓", "受压"])
    extra_vals["bolt_d"] = st.sidebar.number_input("螺栓公称直径 d (mm)", value=12.0)
    extra_vals["e1"] = st.sidebar.number_input("端距 e1 (mm)", value=55.0)
    extra_vals["e2"] = st.sidebar.number_input("侧距 e2 (mm)", value=25.0)
    extra_vals["s"] = st.sidebar.number_input("相邻排距 s (mm)", value=50.0)
    extra_vals["g"] = st.sidebar.number_input("同排间距 g (mm)", value=50.0)
    extra_vals["ls"] = st.sidebar.number_input("斜间距 ls (mm)", value=40.0)
    extra_vals["n"] = st.sidebar.number_input("同排孔数 n", value=2, step=1)
elif "7.2" in project_sel:
    extra_vals["fct"] = st.sidebar.number_input("胶层抗拉强度设计值 fct (MPa)", value=15.0)
    extra_vals["fcv"] = st.sidebar.number_input("胶层抗剪强度设计值 fcv (MPa)", value=10.0)
    extra_vals["ac"] = st.sidebar.number_input("胶层粘结面积 Ac (mm²)", value=2500.0)
    extra_vals["ic"] = st.sidebar.number_input("胶层区域惯性矩 I (mm⁴)", value=2000000.0)
    extra_vals["y0"] = st.sidebar.number_input("受拉边缘至形心距离 y0 (mm)", value=50.0)
    extra_vals["bm"] = st.sidebar.number_input("节点承受弯矩 M (kN·m)", value=2.0)
elif "7.3" in project_sel:
    extra_vals["h_fcv"] = st.sidebar.number_input("胶层抗剪强度设计值 fcv (MPa)", value=10.0)
    extra_vals["h_ac"] = st.sidebar.number_input("胶层粘结面积 Ac (mm²)", value=2500.0)
    extra_vals["h_d"] = st.sidebar.number_input("螺栓公称直径 d (mm)", value=12.0)
    extra_vals["h_n"] = st.sidebar.number_input("同排螺栓数量 n", value=2, step=1)


# ================= 将原代码的核心计算逻辑完整嵌入类中 =================
class StreamlitCalculatorRunner:
    def __init__(self):
        self.MAT_TABLE = MAT_TABLE_DEF
        self.SUPPORT_FACTOR = SUPPORT_FACTOR
        
        # 组装适配器控件
        self.cb_project = MockCombobox(project_sel)
        self.cb_fiber = MockCombobox(fiber_sel)
        self.cb_grade = MockCombobox(grade_sel)
        self.cb_env = MockCombobox(env_sel)
        self.entry_tg = MockWidget(tg_val)
        self.entry_tmax = MockWidget(tmax_val)
        
        self.mat_entries = {k: MockWidget(v) for k, v in mat_vals_input.items()}
        
        self.cb_section = MockCombobox(section_sel)
        self.cb_sub = MockCombobox(sub_sel)
        self.dim_entries = {k: MockWidget(v) for k, v in dim_vals_input.items()}
        self.entry_length = MockWidget(length_val)
        self.cb_support = MockCombobox(support_sel)
        
        self.is_known_load = MockBooleanVar(is_known_load_val)
        self.entry_load = MockWidget(load_val)
        
        # 专项参数挂载
        if "5.1" in project_sel:
            self.cb_hole_type = MockCombobox(extra_vals.get("hole_type", "无削弱"))
            self.hole_entries = {
                "螺栓公称直径 d (mm):": MockWidget(extra_vals.get("d_bolt", 12.0)),
                "破坏面上同排孔数 n:": MockWidget(extra_vals.get("n_hole", 2)),
                "开孔所在板厚 t (mm):": MockWidget(extra_vals.get("t_plate", 4.8))
            }
        elif "6.1" in project_sel and "受弯" in project_sel:
            self.cb_bend_axis = MockCombobox(extra_vals.get("bend_axis", "绕强轴弯曲 (主轴 x-x)"))
            self.entry_lb = MockWidget(extra_vals.get("l_b", 2500.0))
            self.entry_betab = MockWidget(extra_vals.get("beta_b", 1.0))
            self.entry_fv = MockWidget(extra_vals.get("fv", 5000.0))
            self.cb_load_cond = MockCombobox(extra_vals.get("load_cond", "梁端简支, 满布均布荷载"))
        elif "6.5" in project_sel:
            self.cb_conc_type = MockCombobox(extra_vals.get("conc_type", "集中受压荷载 (6.5.2)"))
            self.entry_leff = MockWidget(extra_vals.get("leff", 100.0))
        elif "6.6" in project_sel or "6.7" in project_sel or "6.8" in project_sel:
            self.entry_mx = MockWidget(extra_vals.get("mx", 20.0))
            self.entry_my = MockWidget(extra_vals.get("my", 5.0))
        elif "7.1" in project_sel:
            self.cb_bolt_case = MockCombobox(extra_vals.get("bolt_case", "受拉，单排螺栓"))
            self.entry_bolt_d = MockWidget(extra_vals.get("bolt_d", 12.0))
            self.entry_e1 = MockWidget(extra_vals.get("e1", 55.0))
            self.entry_e2 = MockWidget(extra_vals.get("e2", 25.0))
            self.entry_s = MockWidget(extra_vals.get("s", 50.0))
            self.entry_g = MockWidget(extra_vals.get("g", 50.0))
            self.entry_ls = MockWidget(extra_vals.get("ls", 40.0))
            self.entry_n = MockWidget(extra_vals.get("n", 2))
        elif "7.2" in project_sel:
            self.entry_fct = MockWidget(extra_vals.get("fct", 15.0))
            self.entry_fcv = MockWidget(extra_vals.get("fcv", 10.0))
            self.entry_ac = MockWidget(extra_vals.get("ac", 2500.0))
            self.entry_ic = MockWidget(extra_vals.get("ic", 2000000.0))
            self.entry_y0 = MockWidget(extra_vals.get("y0", 50.0))
            self.entry_bm = MockWidget(extra_vals.get("bm", 2.0))
        elif "7.3" in project_sel:
            self.entry_h_fcv = MockWidget(extra_vals.get("h_fcv", 10.0))
            self.entry_h_ac = MockWidget(extra_vals.get("h_ac", 2500.0))
            self.entry_h_d = MockWidget(extra_vals.get("h_d", 12.0))
            self.entry_h_n = MockWidget(extra_vals.get("h_n", 2))

    # --- 以下完全复用您原代码中的计算辅助方法 ---
    def get_gamma_e(self):
        fiber = self.cb_fiber.get()
        env = self.cb_env.get()
        if "碳纤维" in fiber:
            return {"室内环境": 1.0, "一般室外环境": 1.1, "侵蚀/浸水/海洋环境": 1.2}[env]
        else:
            return {"室内环境": 1.25, "一般室外环境": 1.4, "侵蚀/浸水/海洋环境": 1.6}[env]

    def get_gamma_T(self, tg, tmax):
        if tmax <= tg - 20:
            return 1.0, "Tmax <= Tg-20℃，取值 1.0"
        elif tmax >= tg:
            return 1.6, "Tmax >= Tg，取值 1.6"
        else:
            return 1.0 + 0.6 * (tmax - (tg - 20)) / 20, "插值"

    def get_section_props(self):
        section = self.cb_section.get()
        try:
            if section == "矩形管":
                v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                H = max(v1, v2)
                B = min(v1, v2)
                ag = H * B - (H - 2*t1) * (B - 2*t2)
                iy = (B * H**3 - (B - 2*t2) * (H - 2*t1)**3) / 12
            elif section == "圆管":
                d_val, t = float(self.dim_entries["外径 D (mm):"].get()), float(self.dim_entries["壁厚 t (mm):"].get())
                ag = math.pi * (d_val**2 - (d_val - 2*t)**2) / 4
                iy = math.pi * (d_val**4 - (d_val - 2*t)**4) / 64
            elif section == "双槽形":
                h = float(self.dim_entries["总高度 h (mm):"].get())
                b = float(self.dim_entries["总宽度 b (mm):"].get())
                bf = float(self.dim_entries["单翼缘宽度 bf (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - 2 * tf
                ag = 2 * (hw * tw + 2 * bf * tf)
                iy = 2 * (tw * hw**3 / 12 + 2 * (tf * bf**3 / 12 + bf * tf * (b/4)**2))
            elif section == "槽形":
                h, b, tw, tf = float(self.dim_entries["高度 h (mm):"].get()), float(self.dim_entries["宽度 b (mm):"].get()), float(self.dim_entries["腹板厚 tw (mm):"].get()), float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - tf
                ag = b * tf + hw * tw
                iy = b**3 * tf / 12 + hw * tw**3 / 12
            elif section == "角形":
                h_val, b_val, t = float(self.dim_entries["高度/肢1 h (mm):"].get()), float(self.dim_entries["宽度/肢2 b (mm):"].get()), float(self.dim_entries["厚度 t (mm):"].get())
                ag = (h_val + b_val - t) * t
                iy = h_val * t**3 / 12 + b_val * t**3 / 12
            elif section == "工字形":
                h, b, tw, tf = float(self.dim_entries["高度 h (mm):"].get()), float(self.dim_entries["宽度 b (mm):"].get()), float(self.dim_entries["腹板厚 tw (mm):"].get()), float(self.dim_entries["翼缘厚 tf (mm):"].get())
                ag = 2 * b * tf + (h - 2*tf) * tw
                iy = 2 * (tf * b**3 / 12) + (h - 2*tf) * tw**3 / 12
            elif section == "T形":
                h = float(self.dim_entries["总高度 h (mm):"].get())
                b = float(self.dim_entries["翼缘宽度 b (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - tf
                ag = b * tf + hw * tw
                y_f = h - tf / 2
                y_w = hw / 2
                yc = (b * tf * y_f + hw * tw * y_w) / ag
                iy = (b * tf**3 / 12 + b * tf * (y_f - yc)**2) + (tw * hw**3 / 12 + hw * tw * (y_w - yc)**2)
            elif section == "实心截面":
                sub = self.cb_sub.get()
                if sub == "矩形实心":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    b = float(self.dim_entries["宽度 b (mm):"].get())
                    ag = h * b
                    iy = b * h**3 / 12
                elif sub == "正方形实心":
                    a = float(self.dim_entries["边长 a (mm):"].get())
                    ag = a**2
                    iy = a**4 / 12
                elif sub == "圆形实心":
                    d = float(self.dim_entries["直径 d (mm):"].get())
                    ag = math.pi * d**2 / 4
                    iy = math.pi * d**4 / 64
                else:
                    ag, iy = 1.0, 1.0

            r = math.sqrt(iy / ag) if ag > 0 else 0
            return ag, r
        except ValueError:
            return None, None

    def get_bending_props(self, axis_mode):
        section = self.cb_section.get()
        try:
            if section == "矩形管":
                v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                H = max(v1, v2)
                B = min(v1, v2)
                th_H = t1 if v1 >= v2 else t2
                th_B = t2 if v1 >= v2 else t1
                if "强轴" in axis_mode:
                    ix = (B * H**3 - (B - 2*th_B) * (H - 2*th_H)**3) / 12
                    return ix, ix / (H / 2), ix / (H / 2)
                else:
                    iy = (H * B**3 - (H - 2*th_H) * (B - 2*th_B)**3) / 12
                    return iy, iy / (B / 2), iy / (B / 2)
            elif section == "圆管":
                d_val = float(self.dim_entries["外径 D (mm):"].get())
                t = float(self.dim_entries["壁厚 t (mm):"].get())
                i_val = math.pi * (d_val**4 - (d_val - 2*t)**4) / 64
                return i_val, i_val / (d_val / 2), i_val / (d_val / 2)
            elif section == "工字形":
                h = float(self.dim_entries["高度 h (mm):"].get())
                b = float(self.dim_entries["宽度 b (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                if "强轴" in axis_mode:
                    ix = 2 * (b * tf**3 / 12 + b * tf * (h/2 - tf/2)**2) + tw * (h - 2*tf)**3 / 12
                    return ix, ix / (h / 2), ix / (h / 2)
                else:
                    iy = 2 * (tf * b**3 / 12) + (h - 2*tf) * tw**3 / 12
                    return iy, iy / (b / 2), iy / (b / 2)
            elif section == "槽形":
                h = float(self.dim_entries["高度 h (mm):"].get())
                b = float(self.dim_entries["宽度 b (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - 2*tf
                if "强轴" in axis_mode:
                    ix = 2 * (b * tf**3 / 12 + b * tf * (h/2 - tf/2)**2) + tw * hw**3 / 12
                    return ix, ix / (h / 2), ix / (h / 2)
                else:
                    iy = b**3 * tf / 12 + hw * tw**3 / 12
                    return iy, iy / (b / 2), iy / (b / 2)
            elif section == "双槽形":
                h = float(self.dim_entries["总高度 h (mm):"].get())
                b = float(self.dim_entries["总宽度 b (mm):"].get())
                bf = float(self.dim_entries["单翼缘宽度 bf (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - 2 * tf
                if "强轴" in axis_mode:
                    ix = 2 * (tw * hw**3 / 12 + 2 * (bf * tf**3 / 12 + bf * tf * (h/2 - tf/2)**2))
                    return ix, ix / (h / 2), ix / (h / 2)
                else:
                    iy = 2 * (hw * tw**3 / 12 + 2 * (tf * bf**3 / 12 + bf * tf * (b/2 - bf/2)**2))
                    return iy, iy / (b / 2), iy / (b / 2)
            elif section == "角形":
                h_val = float(self.dim_entries["高度/肢1 h (mm):"].get())
                b_val = float(self.dim_entries["宽度/肢2 b (mm):"].get())
                t = float(self.dim_entries["厚度 t (mm):"].get())
                ag = (h_val + b_val - t) * t
                yc = (h_val * t * (h_val/2) + (b_val - t) * t * (t/2)) / ag
                xc = (t * h_val * (t/2) + (b_val - t) * t * ((b_val + t)/2)) / ag
                icx = (t * h_val**3 / 12 + h_val * t * (h_val/2 - yc)**2) + ((b_val - t) * t**3 / 12 + (b_val - t) * t * (t/2 - yc)**2)
                icy = (h_val * t**3 / 12 + h_val * t * (t/2 - xc)**2) + (t * (b_val - t)**3 / 12 + (b_val - t) * t * ((b_val + t)/2 - xc)**2)
                if "强轴" in axis_mode:
                    i_val = max(icx, icy)
                    c_fiber = max(yc, h_val - yc) if i_val == icx else max(xc, b_val - xc)
                    return i_val, i_val / c_fiber, i_val / c_fiber
                else:
                    i_val = min(icx, icy)
                    c_fiber = max(yc, h_val - yc) if i_val == icy else max(xc, b_val - xc)
                    return i_val, i_val / c_fiber, i_val / c_fiber
            elif section == "T形":
                h = float(self.dim_entries["总高度 h (mm):"].get())
                b = float(self.dim_entries["翼缘宽度 b (mm):"].get())
                tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                hw = h - tf
                if "强轴" in axis_mode:
                    a_f = b * tf
                    a_w = hw * tw
                    y_f = h - tf / 2
                    y_w = hw / 2
                    yc = (a_f * y_f + a_w * y_w) / (a_f + a_w)
                    i_f = b * tf**3 / 12 + a_f * (y_f - yc)**2
                    i_w = tw * hw**3 / 12 + a_w * (y_w - yc)**2
                    ix = i_f + i_w
                    return ix, ix / yc, ix / (h - yc)
                else:
                    iy = (tf * b**3) / 12 + (hw * tw**3) / 12
                    return iy, iy / (b / 2), iy / (b / 2)
            elif section == "实心截面":
                sub = self.cb_sub.get()
                if sub == "矩形实心":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    b = float(self.dim_entries["宽度 b (mm):"].get())
                    if "强轴" in axis_mode:
                        ix = b * h**3 / 12
                        return ix, ix / (h / 2), ix / (h / 2)
                    else:
                        iy = h * b**3 / 12
                        return iy, iy / (b / 2), iy / (b / 2)
                elif sub == "正方形实心":
                    a = float(self.dim_entries["边长 a (mm):"].get())
                    i_val = a**4 / 12
                    return i_val, i_val / (a / 2), i_val / (a / 2)
                elif sub == "圆形实心":
                    d = float(self.dim_entries["直径 d (mm):"].get())
                    i_val = math.pi * d**4 / 64
                    return i_val, i_val / (d / 2), i_val / (d / 2)
            return 1.0, 1.0, 1.0
        except ValueError:
            return None, None, None

    # --- 核心计算逻辑方法（完全保留您原代码中的全部逻辑与文本输出） ---
    def run_calculation_logic(self):
        project = self.cb_project.get()
        text_out = MockTextOut()

        if "待开发" in project:
            text_out.insert(0, f"【系统提示】 {project} 模块正在加紧开发中，敬请期待！\n")
            return text_out.get_result()

        text_out.insert(0, f"================ 计算报告 ({project}) ================\n\n")
        is_all_passed = True

        try:
            mat_vals = {key: float(ent.get()) for key, ent in self.mat_entries.items()}
            gamma_e = self.get_gamma_e()
            tg, tmax = float(self.entry_tg.get()), float(self.entry_tmax.get())
            gamma_T, _ = self.get_gamma_T(tg, tmax)
            
            fd_t = mat_vals["f_L_t"] / (1.25 * gamma_e * gamma_T)
            fd_c = mat_vals["f_L_c"] / (1.25 * gamma_e * gamma_T)
            fd_sh = mat_vals["f_sh"] / (1.25 * gamma_e * gamma_T)
            f_lt_d = mat_vals["f_LT"] / (1.25 * gamma_e * gamma_T)

            ag, r = self.get_section_props()
            if ag is None or ag <= 0:
                text_out.insert(0, "错误：截面尺寸输入无效，请检查数值！\n")
                return text_out.get_result()

            length = float(self.entry_length.get())
            l0 = length * self.SUPPORT_FACTOR[self.cb_support.get()]
            slenderness = l0 / r

            # === 5.1 轴心受拉计算 ===
            if "5.1" in project:
                text_out.insert(0, "[1. 材料与设计强度计算]\n")
                text_out.insert(0, f"  纵向拉伸强度标准值 f_L^t = {mat_vals['f_L_t']} MPa\n")
                text_out.insert(0, f"  综合调整系数: γ_f = 1.25, γ_e = {gamma_e}, γ_T = {gamma_T:.3f}\n")
                text_out.insert(0, f"  计算式: fd,t = f_k / (γ_f × γ_e × γ_T) = {fd_t:.2f} MPa\n\n")
                
                hole_type = self.cb_hole_type.get()
                if hole_type == "无削弱":
                    an = ag
                    k_factor = 1.0
                else:
                    d = float(self.hole_entries["螺栓公称直径 d (mm):"].get())
                    n_hole = int(self.hole_entries["破坏面上同排孔数 n:"].get())
                    t_plate = float(self.hole_entries["开孔所在板厚 t (mm):"].get())
                    d_calc = d + 2.0
                    an_calc = ag - n_hole * d_calc * t_plate
                    an = max(an_calc, 0.75 * ag)
                    k_factor = 0.7
                    if an_calc < 0.75 * ag: is_all_passed = False

                text_out.insert(0, "[2. 截面参数与长细比]\n")
                text_out.insert(0, f"  毛面积 Ag = {ag:.2f} mm² | 净面积 An = {an:.2f} mm² | 折减系数 k = {k_factor}\n")
                text_out.insert(0, f"  计算长度 l0 = {l0:.1f} mm | 回转半径 r = {r:.2f} mm | 长细比 λ = {slenderness:.1f}\n\n")

                if slenderness > 300:
                    text_out.insert(0, f"❌ 长细比 {slenderness:.1f} > 300，不满足规程要求！\n")
                    is_all_passed = False

                n_c = 0.9 * k_factor * an * fd_t / 1000
                text_out.insert(0, "[3. 抗拉承载力计算 (规程 5.1.1)]\n")
                text_out.insert(0, f"  计算式(5.1.1-2): Nc = 0.9 × k × An × fd,t = 0.9 × {k_factor} × {an:.2f} × {fd_t:.2f} / 1000\n")
                text_out.insert(0, f"  结果: 最高抗拉承载力 Nc = {n_c:.2f} kN\n\n")

                if self.is_known_load.get():
                    n_design = float(self.entry_load.get())
                    text_out.insert(0, f"  输入轴力设计值 N = {n_design:.2f} kN\n")
                    if n_design > n_c: 
                        text_out.insert(0, "  ❌ 警告：构件抗拉承载力不足 (N > Nc)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：N <= Nc\n")

            # === 5.2 轴心受压计算 ===
            elif "5.2" in project:
                section_type = self.cb_section.get()
                sub_type = self.cb_sub.get() if section_type == "实心截面" else ""
                display_sec_name = f"实心截面({sub_type})" if section_type == "实心截面" else section_type

                el_c = mat_vals["E_L_c"]
                et_c = mat_vals["E_T_c"]
                g_lt = mat_vals["G_LT"]
                nu_lt = 0.3

                text_out.insert(0, "[1. 材料弹性常数与抗压强度 (规范表 3.3.5)]\n")
                text_out.insert(0, f"  纵向压弹模 E_L^c = {el_c} MPa | 横向压弹模 E_T^c = {et_c} MPa\n")
                text_out.insert(0, f"  抗压设计强度 fd,c = f_k / (1.25 × γ_e × γ_T) = {fd_c:.2f} MPa\n\n")

                text_out.insert(0, "[2. 截面参数与长细比]\n")
                text_out.insert(0, f"  截面类型: {display_sec_name} | 毛面积 Ag = {ag:.2f} mm² | 回转半径 r = {r:.2f} mm\n")
                text_out.insert(0, f"  计算长度 l0 = {l0:.1f} mm | 长细比 λ = {slenderness:.1f}\n\n")

                n_s = 0.9 * ag * fd_c / 1000
                text_out.insert(0, "[3. 材料受压破坏极限承载力 (式 5.2.1-3)]\n")
                text_out.insert(0, f"  计算式: Ns = 0.9 × Ag × fd,c = 0.9 × {ag:.2f} × {fd_c:.2f} / 1000\n")
                text_out.insert(0, f"  结果: 材料受压极限 Ns = {n_s:.2f} kN\n\n")

                n_cr1 = 0.7 * (math.pi**2 * el_c / (slenderness**2)) * ag / 1000
                text_out.insert(0, "[4. 整体稳定极限承载力 (规程 5.2.2)]\n")
                text_out.insert(0, f"  计算式(5.2.4-1): Ncr1 = 0.7 × [ (π² · E_L^c) / λ² ] · Ag = 0.7 × [ (π² × {el_c}) / {slenderness:.1f}² ] × {ag:.2f} / 1000\n")
                text_out.insert(0, f"  结果: 整体稳定极限 Ncr1 = {n_cr1:.2f} kN\n\n")

                n_cr2 = float('inf')
                if section_type == "矩形管":
                    v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                    v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                    t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                    t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                    H = max(v1, v2)
                    B = min(v1, v2)
                    th_H = t1 if v1 >= v2 else t2
                    th_B = t2 if v1 >= v2 else t1
                    beta_w = max(H/th_H, B/th_B)
                    term_root = el_c * et_c + nu_lt * et_c + 2 * g_lt
                    n_cr2 = 0.22 * (math.sqrt(max(term_root, 0)) / (beta_w**2)) * ag / 1000
                    text_out.insert(0, "[5. 局部稳定极限承载力 (规程 5.2.4)]\n")
                    text_out.insert(0, f"  宽厚比 βw = {beta_w:.2f} -> 局部稳定极限 Ncr2 = {n_cr2:.2f} kN (式 5.2.4-2)\n\n")

                n_cc = min(n_s, n_cr1, n_cr2)
                text_out.insert(0, "[6. 轴心受压承载力综合评定 (规程 5.2.1)]\n")
                text_out.insert(0, f"  比选过程(式 5.2.1-2): Nc = min(Ns, Ncr1, Ncr2) = min({n_s:.2f}, {n_cr1:.2f}, {n_cr2 if n_cr2!=float('inf') else '∞'})\n")
                text_out.insert(0, f"  结果: 最终轴心受压承载力 Nc = {n_cc:.2f} kN\n\n")

                if self.is_known_load.get():
                    n_design = float(self.entry_load.get())
                    text_out.insert(0, f"  输入轴力设计值 N = {n_design:.2f} kN\n")
                    if n_design > n_cc:
                        text_out.insert(0, "  ❌ 警告：构件轴压承载力不足 (N > Nc)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：N <= Nc\n")

            # === 6.1 受弯计算 ===
            elif "6.1" in project and "受弯" in project:
                section_type = self.cb_section.get()
                sub_type = self.cb_sub.get() if section_type == "实心截面" else ""
                display_sec_name = f"实心截面({sub_type})" if section_type == "实心截面" else section_type
                
                axis_mode = self.cb_bend_axis.get()
                l_b = float(self.entry_lb.get())
                beta_b = float(self.entry_betab.get())

                el_c = mat_vals["E_L_c"]
                et_c = mat_vals["E_T_c"]
                g_lt = mat_vals["G_LT"]
                nu_lt = 0.3

                text_out.insert(0, "[1. 材料设计强度 (第6章受弯通用)]\n")
                text_out.insert(0, f"  纵向抗拉强度设计值 fd,t = {fd_t:.2f} MPa\n")
                text_out.insert(0, f"  纵向抗压强度设计值 fd,c = {fd_c:.2f} MPa\n\n")

                i_bend, wx_t, wx_c = self.get_bending_props(axis_mode)
                if i_bend is None or i_bend <= 0:
                    text_out.insert(0, f"错误：截面尺寸输入无效或暂不支持【{section_type}】的受弯验算。\n")
                    return text_out.get_result()

                text_out.insert(0, f"[2. 截面抗弯特性 ({axis_mode})]\n")
                text_out.insert(0, f"  截面类型: {display_sec_name}\n")
                text_out.insert(0, f"  计算轴向惯性矩 I = {i_bend:.2e} mm⁴\n")
                text_out.insert(0, f"  受拉侧截面抵抗矩 Wx,t = {wx_t:.2f} mm³\n")
                text_out.insert(0, f"  受压侧截面抵抗矩 Wx,c = {wx_c:.2f} mm³\n\n")

                ms_t = wx_t * fd_t / 1e6
                ms_c = wx_c * fd_c / 1e6
                ms = min(ms_t, ms_c) * 0.9
                text_out.insert(0, "[3. 截面材料抗弯极限承载力计算 (规程 6.1.2)]\n")
                text_out.insert(0, f"  受拉破坏极限 M_s,t = 0.9 × Wx,t × fd,t = 0.9 × {wx_t:.2f} × {fd_t:.2f} / 10^6 = {ms_t*0.9:.2f} kN·m\n")
                text_out.insert(0, f"  受压破坏极限 M_s,c = 0.9 × Wx,c × fd,c = 0.9 × {wx_c:.2f} × {fd_c:.2f} / 10^6 = {ms_c*0.9:.2f} kN·m\n")
                text_out.insert(0, f"  比选过程: Ms = min(M_s,t, M_s,c) = min({ms_t*0.9:.2f}, {ms_c*0.9:.2f}) (式 6.1.2)\n")
                text_out.insert(0, f"  结果: 截面材料抗弯极限 Ms = {ms:.2f} kN·m\n\n")

                m_cr1 = float('inf')
                text_out.insert(0, "[4. 整体稳定极限弯矩详细计算 (规程 6.2)]\n")
                if "强轴" in axis_mode:
                    if section_type == "矩形管":
                        v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                        v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                        t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                        t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                        H = max(v1, v2)
                        B = min(v1, v2)
                        th_H = t1 if v1 >= v2 else t2
                        th_B = t2 if v1 >= v2 else t1
                        iy = (H * B**3 - (H - 2*th_H) * (B - 2*th_B)**3) / 12
                        d_j = 4 * ((B - th_B)**2 * (H - th_H)**2) * (g_lt / 8 * (th_B / B + th_H / H))
                        m_cr1 = 0.56 * beta_b * math.sqrt(math.pi**2 * el_c * iy * d_j / (l_b**2)) / 1e6
                        text_out.insert(0, f"  • 弱轴惯性矩 Iy = {iy:.2e} mm⁴, 扭转刚度 Dj = {d_j:.2e} N·mm²\n")
                        text_out.insert(0, f"  • 计算式(6.2.3-1): Mcr1 = 0.56 × βb × √(π² · El_c · Iy · Dj / Lb²) / 10^6\n")
                        text_out.insert(0, f"  结果: 整体稳定极限 M_cr1 = {m_cr1:.2f} kN·m\n\n")
                    else:
                        text_out.insert(0, "  提示: 此截面强轴整体稳定按规范基础公式计算。\n\n")
                else:
                    if section_type == "矩形管":
                        v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                        v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                        t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                        t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                        H = max(v1, v2)
                        B = min(v1, v2)
                        th_H = t1 if v1 >= v2 else t2
                        th_B = t2 if v1 >= v2 else t1
                        ix_strong = (B * H**3 - (B - 2*th_B) * (H - 2*th_H)**3) / 12
                        d_j = 4 * ((B - th_B)**2 * (H - th_H)**2) * (g_lt / 8 * (th_B / B + th_H / H))
                        m_cr1 = 0.56 * beta_b * math.sqrt(math.pi**2 * el_c * ix_strong * d_j / (l_b**2)) / 1e6
                        text_out.insert(0, f"  • 弱轴弯曲整体稳定 (基于Ix约束): M_cr1 = {m_cr1:.2f} kN·m\n\n")
                    else:
                        m_cr1 = 100.0

                m_cr2 = float('inf')
                text_out.insert(0, "[5. 局部稳定极限弯矩详细计算 (规程 6.3)]\n")
                if section_type == "矩形管":
                    v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                    v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                    t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                    t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                    H = max(v1, v2)
                    B = min(v1, v2)
                    th_H = t1 if v1 >= v2 else t2
                    th_B = t2 if v1 >= v2 else t1
                    if "强轴" in axis_mode:
                        k_r = (et_c * th_B**3 / (3 * H)) * (1 - (th_H**2 * H**2) / (6 * th_B**2 * B**2))
                        k_r = max(k_r, 0.001)
                        xi = 1.0 / (1 + (4 * et_c * th_H**3) / (5 * B * k_r))
                        term1 = math.sqrt(el_c * et_c * (1 + 4.1 * xi)) / 6
                        term2 = (2 + 0.62 * xi**2) * (et_c * nu_lt / 12 + g_lt / 6)
                        f_cr_f = (4 * math.pi**2 * th_H**2 / B**2) * (term1 + term2)
                        f_cr_w = (2 * math.pi**2 * th_B**2 / H**2) * (1.25 * math.sqrt(el_c * et_c) + et_c * nu_lt + 2 * g_lt)
                        f_cr = min(f_cr_f, f_cr_w)
                        text_out.insert(0, f"  • 强轴局部屈曲(式6.3.6): 受压翼缘 fcr,f = {f_cr_f:.2f} MPa, 腹板 fcr,w = {f_cr_w:.2f} MPa\n")
                    else:
                        f_cr = (4 * th_H**2 / H**2) * g_lt
                        text_out.insert(0, f"  • 弱轴局部屈曲: fcr = {f_cr:.2f} MPa\n")
                    
                    m_cr2 = 0.8 * f_cr * wx_c / 1e6
                    text_out.insert(0, f"  结果: 局部稳定极限 M_cr2 = 0.8 × {f_cr:.2f} × {wx_c:.2f} / 10^6 = {m_cr2:.2f} kN·m (式 6.3.2)\n\n")

                m_u = min(ms, m_cr1, m_cr2)
                text_out.insert(0, "[6. 受弯承载力综合评定 (规程 6.1.1)]\n")
                text_out.insert(0, f"  控制标准(式 6.1.1-2): Mu = min(Ms, M_cr1, M_cr2) = min({ms:.2f}, {m_cr1 if m_cr1!=float('inf') else '∞'}, {m_cr2 if m_cr2!=float('inf') else '∞'})\n")
                text_out.insert(0, f"  结果: 最终受弯承载力 Mu = {m_u:.2f} kN·m\n\n")

                if self.is_known_load.get():
                    m_design = float(self.entry_load.get())
                    text_out.insert(0, f"  输入弯矩设计值 M = {m_design:.2f} kN·m\n")
                    if m_design > m_u:
                        text_out.insert(0, "  ❌ 警告：构件受弯承载力不足 (M > Mu)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：M <= Mu\n")

                # === 7. 挠度变形验算 (规程 6.1.6 ~ 6.1.7) ===
                text_out.insert(0, "\n[7. 受弯构件挠度变形验算 (规程 6.1.6)]\n")
                try:
                    fv_val = float(self.entry_fv.get())
                    load_cond_str = self.cb_load_cond.get()
                    
                    k_map = {
                        "梁端简支, 满布均布荷载": (5.0/384.0, 1.0/8.0),
                        "梁端简支, 跨中集中荷载": (1.0/48.0, 1.0/4.0),
                        "悬臂端承受集中荷载": (1.0/3.0, 1.0),
                        "悬臂端承受均布荷载": (1.0/8.0, 1.0/2.0),
                        "梁端固结, 满布均布荷载": (1.0/384.0, 1.0/24.0)
                    }
                    k1, k2 = k_map.get(load_cond_str, (5.0/384.0, 1.0/8.0))
                    
                    el_t = mat_vals["E_L_t"]
                    g_lt_val = mat_vals["G_LT"]
                    
                    as_area_def = ag * 0.5
                    if section_type == "矩形管":
                        v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                        v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                        t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                        H = max(v1, v2)
                        as_area_def = 2.0 * (H - 2*t1) * t1
                    elif section_type == "工字形":
                        h = float(self.dim_entries["高度 h (mm):"].get())
                        tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                        tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                        as_area_def = (h - 2*tf) * tw
                    elif section_type == "槽形":
                        h = float(self.dim_entries["高度 h (mm):"].get())
                        tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                        tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                        as_area_def = (h - tf) * tw

                    eb = el_t
                    gb = g_lt_val * (as_area_def / ag) if ag > 0 else g_lt_val
                    
                    db = (k1 * fv_val * (length**3)) / (eb * i_bend)
                    ds = (k2 * fv_val * length) / (as_area_def * gb) if as_area_def * gb > 0 else 0.0
                    d_total = db + ds
                    
                    allowable_ratio = 250.0
                    allowable_deflection = length / allowable_ratio
                    
                    text_out.insert(0, f"  • 竖向荷载标准值 Fv = {fv_val:.1f} N, 跨度 L = {length:.1f} mm\n")
                    text_out.insert(0, f"  • 荷载工况: {load_cond_str} (k1 = {k1:.5f}, k2 = {k2:.5f})\n")
                    text_out.insert(0, f"  • 全截面模量: Eb = EL = {eb:.1f} MPa (式6.1.7-1), Gb = {gb:.2f} MPa (式6.1.7-2)\n")
                    text_out.insert(0, f"  • 弯曲效应挠度 db = k1·Fv·L³ / (Eb·I) = {db:.4f} mm (式 6.1.6-1)\n")
                    text_out.insert(0, f"  • 剪切效应挠度 ds = k2·Fv·L / (As·Gb) = {ds:.4f} mm (式 6.1.6-2)\n")
                    text_out.insert(0, f"  • 总挠度叠加 d_total = db + ds = {d_total:.4f} mm (规程 6.1.6)\n")
                    text_out.insert(0, f"  • 容许挠度限值 [d] = L / 250 = {length} / 250 = {allowable_deflection:.2f} mm\n")
                    
                    if d_total > allowable_deflection:
                        text_out.insert(0, "  ❌ 警告：受弯构件挠度超出规范限值 (d_total > [d])!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 挠度校验通过：d_total <= [d]\n")
                except Exception as ex:
                    text_out.insert(0, f"  ⚠️ 挠度计算参数填写有误，跳过挠度验算。详情: {str(ex)}\n")

            # === 6.1 受剪计算 (规范第6.1节) ===
            elif "6.1" in project and "受剪" in project:
                section_type = self.cb_section.get()
                sub_type = self.cb_sub.get() if section_type == "实心截面" else ""
                display_sec_name = f"实心截面({sub_type})" if section_type == "实心截面" else section_type

                el_c = mat_vals["E_L_c"]
                et_c = mat_vals["E_T_c"]
                g_lt = mat_vals["G_LT"]
                nu_lt = 0.3

                text_out.insert(0, "[1. 面内剪切强度设计值计算 (规范 6.1.4)]\n")
                text_out.insert(0, f"  面内剪切强度标准值 f_LT = {mat_vals['f_LT']} MPa\n")
                text_out.insert(0, f"  综合调整系数: γ_f = 1.25, γ_e = {gamma_e}, γ_T = {gamma_T:.3f}\n")
                text_out.insert(0, f"  计算式: f_LT,d = f_LT / (γ_f × γ_e × γ_T) = {mat_vals['f_LT']} / (1.25 × {gamma_e} × {gamma_T:.3f}) = {f_lt_d:.2f} MPa\n\n")

                as_area = 0.0
                h_val_for_beta = 100.0
                t_val_for_beta = 1.0
                text_out.insert(0, "[2. 腹板面积 As 与高厚比 βw 计算]\n")
                if section_type == "矩形管":
                    v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                    v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                    t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                    H = max(v1, v2)
                    as_area = 2.0 * (H - 2*t1) * t1
                    h_val_for_beta = H - 2*t1
                    t_val_for_beta = t1
                    text_out.insert(0, f"  矩形管腹板面积 As = 2 × (H - 2×t1) × t1 = 2 × ({H} - 2×{t1}) × {t1} = {as_area:.2f} mm²\n")
                elif section_type == "工字形":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                    tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                    as_area = (h - 2*tf) * tw
                    h_val_for_beta = h - 2*tf
                    t_val_for_beta = tw
                    text_out.insert(0, f"  工字形腹板面积 As = (h - 2×tf) × tw = ({h} - 2×{tf}) × {tw} = {as_area:.2f} mm²\n")
                elif section_type == "槽形":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                    tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                    as_area = (h - tf) * tw
                    h_val_for_beta = h - tf
                    t_val_for_beta = tw
                    text_out.insert(0, f"  槽形腹板面积 As = (h - tf) × tw = ({h} - {tf}) × {tw} = {as_area:.2f} mm²\n")
                else:
                    as_area = ag * 0.5
                    h_val_for_beta = length
                    t_val_for_beta = 5.0
                    text_out.insert(0, f"  折算腹板面积 As = 0.5 × Ag = {as_area:.2f} mm²\n")

                beta_w = h_val_for_beta / t_val_for_beta if t_val_for_beta > 0 else 1.0
                text_out.insert(0, f"  腹板高厚比 βw = h_w / t_w = {h_val_for_beta:.1f} / {t_val_for_beta} = {beta_w:.2f}\n\n")

                v_r = 0.9 * as_area * f_lt_d / 1000.0
                text_out.insert(0, "[3. 受剪材料破坏承载力计算 (规程 6.1.4)]\n")
                text_out.insert(0, f"  计算式(6.1.4): Vr = 0.9 × As × f_LT,d = 0.9 × {as_area:.2f} × {f_lt_d:.2f} / 1000\n")
                text_out.insert(0, f"  结果: 受剪材料破坏承载力 Vr = {v_r:.2f} kN\n\n")

                text_out.insert(0, "[4. 受剪局部稳定极限承载力计算 (规程 6.4.1 ~ 6.4.2)]\n")
                left_expr = 2 * g_lt + et_c * nu_lt
                right_expr = math.sqrt(el_c * et_c)
                text_out.insert(0, f"  判断条件计算: 2·G_LT + E_T^c·ν_LT = 2×{g_lt} + {et_c}×{nu_lt} = {left_expr:.2f}\n")
                text_out.insert(0, f"  对比基准: √(E_L^c · E_T^c) = √({el_c} × {et_c}) = {right_expr:.2f}\n")

                if left_expr <= right_expr:
                    inner_term = 8.1 + 5.0 * (left_expr / right_expr)
                    k_lt = (el_c / et_c)**0.25 * math.sqrt(inner_term)
                    text_out.insert(0, f"  分支判定: 2·G_LT + E_T^c·ν_LT <= √(E_L^c · E_T^c)，套用式 (6.4.2-1)\n")
                else:
                    k_lt = math.sqrt(nu_lt + (2 * g_lt / et_c) * (11.7 + 1.4 * ((right_expr / left_expr)**2)))
                    text_out.insert(0, f"  分支判定: 2·G_LT + E_T^c·ν_LT > √(E_L^c · E_T^c)，套用式 (6.4.2-2)\n")

                text_out.insert(0, f"  计算得到: 受剪屈曲刚度系数 k_LT = {k_lt:.4f}\n")

                v_cr = (k_lt * et_c * as_area) / (5.0 * (beta_w**2)) / 1000.0
                text_out.insert(0, f"  计算式(6.4.1): Vcr = (k_LT · E_T^c · As) / (5 · βw²) / 1000\n")
                text_out.insert(0, f"               = ({k_lt:.4f} × {et_c} × {as_area:.2f}) / (5 × {beta_w:.2f}²) / 1000 = {v_cr:.2f} kN\n\n")

                v_u = min(v_r, v_cr)
                text_out.insert(0, "[5. 受剪承载力综合评定]\n")
                text_out.insert(0, f"  控制标准(式 6.1.3-2): Vu = min(Vr, Vcr) = min({v_r:.2f}, {v_cr:.2f})\n")
                text_out.insert(0, f"  结果: 最终抗剪承载力 Vu = {v_u:.2f} kN\n\n")

                if self.is_known_load.get():
                    v_design = float(self.entry_load.get())
                    text_out.insert(0, f"  输入剪力设计值 V = {v_design:.2f} kN\n")
                    if v_design > v_u:
                        text_out.insert(0, "  ❌ 警告：构件抗剪承载力不足 (V > Vu)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：V <= Vu\n")

            # === 6.1 受扭计算 (规范第6.1节) ===
            elif "6.1" in project and "受扭" in project:
                text_out.insert(0, "[1. 面内剪切强度设计值计算 (规范 6.1.5)]\n")
                text_out.insert(0, f"  面内剪切强度标准值 f_LT = {mat_vals['f_LT']} MPa\n")
                text_out.insert(0, f"  综合调整系数: γ_f = 1.25, γ_e = {gamma_e}, γ_T = {gamma_T:.3f}\n")
                text_out.insert(0, f"  计算式: f_LT,d = f_LT / (γ_f × γ_e × γ_T) = {mat_vals['f_LT']} / (1.25 × {gamma_e} × {gamma_T:.3f}) = {f_lt_d:.2f} MPa\n\n")

                section_type = self.cb_section.get()
                text_out.insert(0, "[2. 圣维南扭转常数 J 计算 (规程表 6.1.5)]\n")
                
                j_val = 0.0
                t_char = 1.0
                
                if section_type == "矩形管":
                    v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                    v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                    t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                    t2 = float(self.dim_entries["宽度壁厚 t2 (mm):"].get())
                    H = max(v1, v2)
                    B = min(v1, v2)
                    th_H = t1 if v1 >= v2 else t2
                    th_B = t2 if v1 >= v2 else t1
                    
                    h_center = H - th_H
                    b_center = B - th_B
                    area_enclosed = h_center * b_center
                    j_val = (2.0 * (area_enclosed**2)) / ((H / th_H) + (B / th_H))
                    t_char = min(th_H, th_B)
                    
                    text_out.insert(0, f"  • 矩形管中心线尺寸: h_c = H - t_H = {h_center:.1f} mm, b_c = B - t_B = {b_center:.1f} mm\n")
                    text_out.insert(0, f"  • 围堡面积 A = h_c × b_c = {area_enclosed:.2f} mm²\n")
                    text_out.insert(0, f"  • 表 6.1.5 方管公式: J = 2·A² / (h/t_w + b/t_f)\n")
                    text_out.insert(0, f"    J = 2 × ({area_enclosed:.2f})² / [ ({H}/{th_H}) + ({B}/{th_B}) ] = {j_val:.2e} mm⁴\n")
                    text_out.insert(0, f"  • 特征厚度 t = min(t1, t2) = {t_char} mm\n\n")

                elif section_type == "圆管":
                    d_val = float(self.dim_entries["外径 D (mm):"].get())
                    t = float(self.dim_entries["壁厚 t (mm):"].get())
                    j_val = (math.pi / 32.0) * (d_val**4 - (d_val - 2*t)**4)
                    t_char = t
                    text_out.insert(0, f"  • 表 6.1.5 圆管公式: J = (π / 32) · [ D⁴ - (D - 2t)⁴ ]\n")
                    text_out.insert(0, f"    J = (π / 32) × [ {d_val}⁴ - ({d_val - 2*t})⁴ ] = {j_val:.2e} mm⁴\n")
                    text_out.insert(0, f"  • 特征厚度 t = 壁厚 = {t} mm\n\n")

                elif section_type == "工字形":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    b = float(self.dim_entries["宽度 b (mm):"].get())
                    tw = float(self.dim_entries["腹板厚 tw (mm):"].get())
                    tf = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                    hw = h - 2 * tf
                    j_val = (1.0 / 3.0) * (2 * b * (tf**3) + hw * (tw**3))
                    t_char = max(tf, tw)
                    text_out.insert(0, f"  • 表 6.1.5 工字形公式: J = (1/3) · (2 · b_f · t_f³ + h_w · t_w³)\n")
                    text_out.insert(0, f"    J = (1/3) × (2 × {b} × {tf}³ + {hw} × {tw}³) = {j_val:.2e} mm⁴\n")
                    text_out.insert(0, f"  • 特征厚度 t = max(t_f, t_w) = {t_char} mm\n\n")

                else:
                    j_val = ag * 20.0
                    t_char = 5.0
                    text_out.insert(0, f"  • 通用/折算截面圣维南常数 J = {j_val:.2e} mm⁴, 特征厚度 t = {t_char} mm\n\n")

                t_c = 0.9 * f_lt_d * (j_val / t_char) / 1e6
                text_out.insert(0, "[3. 抗扭承载力计算 (规程 6.1.5-2)]\n")
                text_out.insert(0, f"  计算式(6.1.5-2): Tc = 0.9 × f_LT,d × (J / t) / 10^6\n")
                text_out.insert(0, f"               = 0.9 × {f_lt_d:.2f} × ({j_val:.2e} / {t_char}) / 10^6\n")
                text_out.insert(0, f"  结果: 抗扭承载力设计值 Tc = {t_c:.2f} kN·m\n\n")

                if self.is_known_load.get():
                    t_design = float(self.entry_load.get())
                    text_out.insert(0, f"  输入扭矩设计值 T = {t_design:.2f} kN·m\n")
                    if t_design > t_c:
                        text_out.insert(0, "  ❌ 警告：构件抗扭承载力不足 (T > Tc)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：T <= Tc\n")

            # === 6.5 集中荷载计算 (规范第 6.5 节) ===
            elif "6.5" in project and "集中荷载" in project:
                conc_type = self.cb_conc_type.get()
                leff = float(self.entry_leff.get())
                f_design = float(self.entry_load.get())
                
                text_out.insert(0, "[1. 集中荷载专项参数与假定 (规范第 6.5 节)]\n")
                text_out.insert(0, f"  • 集中荷载分布长度 leff = {leff} mm\n")
                text_out.insert(0, "  • 依据规程 6.5 节假定：集中受拉时腹板承担均匀拉力；集中受压时需综合比选腹板剪切断裂(F1)、腹板受压屈曲(F2)及翼缘受弯(F3)。\n\n")

                section_type = self.cb_section.get()
                tw_val = 4.8
                hw_val = 90.4
                tf_val = 4.8
                if section_type == "矩形管":
                    v1 = float(self.dim_entries["高度尺寸 h (mm):"].get())
                    v2 = float(self.dim_entries["宽度尺寸 b (mm):"].get())
                    t1 = float(self.dim_entries["高度壁厚 t1 (mm):"].get())
                    H = max(v1, v2)
                    tw_val = t1
                    hw_val = H - 2 * t1
                elif section_type == "工字形":
                    h = float(self.dim_entries["高度 h (mm):"].get())
                    tw_val = float(self.dim_entries["腹板厚 tw (mm):"].get())
                    tf_val = float(self.dim_entries["翼缘厚 tf (mm):"].get())
                    hw_val = h - 2 * tf_val

                if "受拉" in conc_type:
                    f_td_t = mat_vals["f_T_t"] / (1.25 * gamma_e * gamma_T)
                    f_limit = leff * tw_val * f_td_t / 1000.0
                    text_out.insert(0, "[2. 集中受拉承载力计算 (规程 6.5.1)]\n")
                    text_out.insert(0, f"  横向拉伸强度设计值 f_T,d^t = {f_td_t:.2f} MPa\n")
                    text_out.insert(0, f"  计算式(6.5.1): F <= leff · tw · f_T,d^t = {leff} × {tw_val} × {f_td_t:.2f} / 1000 = {f_limit:.2f} kN\n\n")
                    text_out.insert(0, f"  输入集中受拉荷载 F = {f_design:.2f} kN\n")
                    if f_design > f_limit:
                        text_out.insert(0, "  ❌ 警告：集中受拉承载力不足 (F > F_limit)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：F <= F_limit\n")
                else:
                    k_val = tf_val + 2.0
                    bw_val = leff
                    f_sh_d = fd_sh
                    
                    f1 = 0.5 * hw_val * tw_val * (1.0 + (2.0 * k_val + 6.0 * tw_val + bw_val) / hw_val) * f_sh_d / 1000.0
                    
                    el_c = mat_vals["E_L_c"]
                    et_c = mat_vals["E_T_c"]
                    g_lt = mat_vals["G_LT"]
                    nu_lt = 0.3
                    f2 = (1.3 * (tw_val**3) / leff) * (math.sqrt(el_c * et_c) + et_c * nu_lt + 2 * g_lt) / 1000.0
                    
                    f_td = min(mat_vals["f_T_c"], mat_vals["f_T_t"]) / (1.25 * gamma_e * gamma_T)
                    be = 2.0 * leff
                    f3 = (be * (tf_val**2) * f_td) / (10.0 * leff) / 1000.0
                    
                    f_limit = min(f1, f2, f3)
                    text_out.insert(0, "[2. 集中受压承载力详细比选 (规程 6.5.2 ~ 6.5.5)]\n")
                    text_out.insert(0, f"  • 腹板剪切断裂承载力 F1 = 0.5·h_w·t_w·[1 + (2k + 6t_w + b_w)/h_w]·f_sh,d = {f1:.2f} kN (式 6.5.3)\n")
                    text_out.insert(0, f"  • 腹板受压屈曲承载力 F2 = [1.3·t_w³ / leff]·[√(E_L^c·E_T^c) + E_T^c·ν_LT + 2G_LT] / 1000 = {f2:.2f} kN (式 6.5.4)\n")
                    text_out.insert(0, f"  • 翼缘受弯承载力 F3 = (be·t_f²·f_T,d) / (10·le) / 1000 = {f3:.2f} kN (式 6.5.5)\n")
                    text_out.insert(0, f"  比选过程(式 6.5.2): F_limit = min(F1, F2, F3) = min({f1:.2f}, {f2:.2f}, {f3:.2f})\n")
                    text_out.insert(0, f"  结果: 集中受压承载力极限 F_limit = {f_limit:.2f} kN\n\n")
                    
                    text_out.insert(0, f"  输入集中受压荷载 F = {f_design:.2f} kN\n")
                    if f_design > f_limit:
                        text_out.insert(0, "  ❌ 警告：集中受压承载力不足 (F > F_limit)!\n")
                        is_all_passed = False
                    else:
                        text_out.insert(0, "  ✔ 校验通过：F <= F_limit\n")

            # === 6.6 / 6.7 / 6.8 组合受力计算 (规范第 6.6 节) ===
            elif "6.6" in project or "6.7" in project or "6.8" in project:
                n_design = float(self.entry_load.get()) # 轴力 N
                mx_design = float(self.entry_mx.get())  # 强轴弯矩 Mx
                my_design = float(self.entry_my.get())  # 弱轴弯矩 My
                
                text_out.insert(0, "[1. 组合受力专项参数与分项验算 (规范第 6.6 节)]\n")
                text_out.insert(0, f"  • 轴向力设计值 N = {n_design:.2f} kN\n")
                text_out.insert(0, f"  • 强轴弯矩设计值 Mx = {mx_design:.2f} kN·m\n")
                text_out.insert(0, f"  • 弱轴弯矩设计值 My = {my_design:.2f} kN·m\n")
                text_out.insert(0, "  • 依据规程 6.6 节假定：弹脆性材料统一采用线性交互方程，各项应力比总和 <= 1.0。\n\n")
                
                if "6.6" in project:
                    an_val = ag
                    nc_val = 0.9 * an_val * fd_t / 1000.0
                    text_out.insert(0, f"  • 拉弯构件抗拉承载力分母 Nc = 0.9·An·fd,t = {nc_val:.2f} kN (规程 5.1.1)\n")
                else:
                    el_c = mat_vals["E_L_c"]
                    ns_val = 0.9 * ag * fd_c / 1000.0
                    ncr1_val = 0.7 * (math.pi**2 * el_c / (slenderness**2)) * ag / 1000.0
                    nc_val = min(ns_val, ncr1_val)
                    text_out.insert(0, f"  • 压弯构件轴压稳定承载力分母 Nc = min(Ns, Ncr1) = {nc_val:.2f} kN (规程 5.2.1)\n")

                _, wx_strong, _ = self.get_bending_props("绕强轴弯曲 (主轴 x-x)")
                _, wy_weak, _ = self.get_bending_props("绕弱轴弯曲 (次轴 y-y)")
                
                mx_c = wx_strong * fd_t * 0.9 / 1e6
                my_c = wy_weak * fd_t * 0.9 / 1e6
                
                text_out.insert(0, f"  • 强轴抗弯承载力分母 Mx,c = 0.9·Wx·fd,t / 10^6 = {mx_c:.2f} kN·m (规程 6.1.2)\n")
                text_out.insert(0, f"  • 弱轴抗弯承载力分母 My,c = 0.9·Wy·fd,t / 10^6 = {my_c:.2f} kN·m (规程 6.1.2)\n\n")

                ratio_n = abs(n_design) / nc_val if nc_val > 0 else 0
                ratio_mx = abs(mx_design) / mx_c if mx_c > 0 else 0
                ratio_my = abs(my_design) / my_c if my_c > 0 else 0
                total_ratio = ratio_n + ratio_mx + ratio_my

                text_out.insert(0, "[2. 线性交互比值综合验算 (规程 6.6.1 / 6.6.2)]\n")
                text_out.insert(0, f"  计算式: (N / Nc) + (Mx / Mx,c) + (My / My,c) <= 1.0\n")
                text_out.insert(0, f"  • 轴力比: N / Nc = {abs(n_design):.2f} / {nc_val:.2f} = {ratio_n:.3f}\n")
                text_out.insert(0, f"  • 强轴弯矩比: Mx / Mx,c = {abs(mx_design):.2f} / {mx_c:.2f} = {ratio_mx:.3f}\n")
                text_out.insert(0, f"  • 弱轴弯矩比: My / My,c = {abs(my_design):.2f} / {my_c:.2f} = {ratio_my:.3f}\n")
                text_out.insert(0, f"  • 交互总比值 = {ratio_n:.3f} + {ratio_mx:.3f} + {ratio_my:.3f} = {total_ratio:.3f} (限值 1.0)\n\n")

                if total_ratio > 1.0:
                    text_out.insert(0, "  ❌ 警告：组合受力超限 (总比值 > 1.0)!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 组合受力验算通过 (总比值 <= 1.0)\n")

            # === 7.1 连接节点设计 (规范第 7.1 节与表 7.1.8) ===
            elif "7.1" in project:
                bolt_case = self.cb_bolt_case.get()
                d_bolt = float(self.entry_bolt_d.get())
                e1 = float(self.entry_e1.get())
                e2 = float(self.entry_e2.get())
                s_pitch = float(self.entry_s.get())
                g_pitch = float(self.entry_g.get())
                ls_val = float(self.entry_ls.get())
                n_count = int(self.entry_n.get())
                v_design = float(self.entry_load.get())

                dn = d_bolt + 2.0 
                
                text_out.insert(0, "[1. 螺栓连接几何构造与最小尺寸验算 (规程表 7.1.8)]\n")
                text_out.insert(0, f"  • 螺栓公称直径 d = {d_bolt} mm, 螺栓孔径 dn = d + 2 = {dn:.1f} mm\n")
                text_out.insert(0, f"  • 输入尺寸: 端距 e1 = {e1} mm, 侧距 e2 = {e2} mm, 排距 s = {s_pitch} mm, 同排间距 g = {g_pitch} mm, 斜间距 ls = {ls_val} mm\n")

                if "受拉" in bolt_case and "单排" in bolt_case:
                    min_e1 = 4.0 * dn
                elif "受拉" in bolt_case and "多排" in bolt_case:
                    min_e1 = 2.0 * dn
                else:
                    min_e1 = 2.0 * dn

                min_e2 = 1.5 * dn
                min_s = 4.0 * dn
                min_g = 4.0 * dn
                min_ls = 2.8 * dn

                text_out.insert(0, f"  • 规范表7.1.8最小端距限值 [e1] = {min_e1 / dn:.1f}·dn = {min_e1:.1f} mm\n")
                text_out.insert(0, f"  • 规范表7.1.8最小侧距限值 [e2] = 1.5·dn = {min_e2:.1f} mm\n")
                text_out.insert(0, f"  • 规范表7.1.8最小排距限值 [s] = 4.0·dn = {min_s:.1f} mm\n")
                text_out.insert(0, f"  • 规范表7.1.8同排间距限值 [g] = 4.0·dn = {min_g:.1f} mm\n")
                text_out.insert(0, f"  • 规范表7.1.8最小斜间距限值 [ls] = 2.8·dn = {min_ls:.1f} mm\n")

                geo_passed = True
                if e1 < min_e1: 
                    text_out.insert(0, f"  ❌ 警告：端距 e1 ({e1}mm) 小于规范最小值 [{min_e1:.1f}mm]!\n")
                    geo_passed = False
                if e2 < min_e2: 
                    text_out.insert(0, f"  ❌ 警告：侧距 e2 ({e2}mm) 小于规范最小值 [{min_e2:.1f}mm]!\n")
                    geo_passed = False
                if s_pitch < min_s: 
                    text_out.insert(0, f"  ❌ 警告：排距 s ({s_pitch}mm) 小于规范最小值 [{min_s:.1f}mm]!\n")
                    geo_passed = False
                if g_pitch < min_g: 
                    text_out.insert(0, f"  ❌ 警告：同排间距 g ({g_pitch}mm) 小于规范最小值 [{min_g:.1f}mm]!\n")
                    geo_passed = False
                if ls_val < min_ls: 
                    text_out.insert(0, f"  ❌ 警告：斜间距 ls ({ls_val}mm) 小于规范最小值 [{min_ls:.1f}mm]!\n")
                    geo_passed = False

                if not geo_passed:
                    text_out.insert(0, "  ⚠️ 注记2提示：当无法满足表中的最小几何尺寸时，应通过计算或试验分析承载力下降。\n\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 节点几何尺寸完全满足表 7.1.8 要求！\n\n")

                text_out.insert(0, "[2. 螺栓节点多模式承载力比选 (规程 7.1.9)]\n")
                plate_t = 6.4
                if hasattr(self, "dim_entries") and len(self.dim_entries) > 0:
                    for k, ent in self.dim_entries.items():
                        if "厚" in k or "t" in k:
                            try:
                                plate_t = float(ent.get())
                            except:
                                pass

                ab_area = math.pi * (d_bolt**2) / 4.0
                f_nv_val = 140.0
                f_br_val = mat_vals["f_L_t"] * 0.6

                n_total = n_count
                n_bt_v = n_total * f_nv_val * ab_area / 1000.0
                n_br = n_total * plate_t * d_bolt * f_br_val / 1000.0
                n_sh = 1.4 * n_total * (e1 - dn / 2.0) * plate_t * f_lt_d / 1000.0

                text_out.insert(0, f"  • 螺栓受剪承载力 Nbt,v = n·f_nv·Ab = {n_bt_v:.2f} kN (式 7.1.9-4)\n")
                text_out.insert(0, f"  • 螺栓孔壁承压承载力 Nbr = n·t·d·f_br = {n_br:.2f} kN (式 7.1.9-5)\n")
                text_out.insert(0, f"  • 端部剪切冲切承载力 Nsh = 1.4·n·(e1 - dn/2)·t·f_LT,d = {n_sh:.2f} kN (式 7.1.9-6)\n")

                node_capacity = min(n_bt_v, n_br, n_sh)
                text_out.insert(0, f"\n[3. 节点抗剪承载力综合评定]\n")
                text_out.insert(0, f"  控制标准: Nu = min(Nbt,v, Nbr, Nsh) = {node_capacity:.2f} kN\n")
                text_out.insert(0, f"  输入节点设计剪力 V = {v_design:.2f} kN\n")

                if v_design > node_capacity:
                    text_out.insert(0, "  ❌ 警告：节点连接承载力不足 (V > Nu)!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 校验通过：V <= Nu\n")

            # === 7.2 粘结连接设计 (规程第 7.2 节) ===
            elif "7.2" in project:
                fct_val = float(self.entry_fct.get())
                fcv_val = float(self.entry_fcv.get())
                ac_val = float(self.entry_ac.get())
                ic_val = float(self.entry_ic.get())
                y0_val = float(self.entry_y0.get())
                bm_val = float(self.entry_bm.get())
                load_val = float(self.entry_load.get())

                text_out.insert(0, "[1. 粘结连接节点强度验算 (规范第 7.2 节)]\n")
                text_out.insert(0, f"  • 胶层抗拉强度设计值 fct = {fct_val:.2f} MPa, 抗剪强度设计值 fcv = {fcv_val:.2f} MPa\n")
                text_out.insert(0, f"  • 胶层粘结面积 Ac = {ac_val:.2f} mm², 截面惯性矩 I = {ic_val:.2e} mm⁴\n\n")

                nc_bond = 0.85 * fct_val * ac_val / 1000.0
                text_out.insert(0, "[2. 受拉粘结验算 (规程 7.2.3)]\n")
                text_out.insert(0, f"  计算式(7.2.3): N <= 0.85 · fct · Ac = 0.85 × {fct_val} × {ac_val} / 1000 = {nc_bond:.2f} kN\n")
                text_out.insert(0, f"  输入拉力设计值 N = {load_val:.2f} kN\n")
                if load_val > nc_bond:
                    text_out.insert(0, "  ❌ 警告：受拉粘结承载力不足!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 受拉粘结校验通过\n\n")

                vc_bond = 0.9 * fcv_val * ac_val / 1000.0
                text_out.insert(0, "[3. 受剪粘结验算 (规程 7.2.4)]\n")
                text_out.insert(0, f"  计算式(7.2.4): V <= 0.9 · fcv · Ac = 0.9 × {fcv_val} × {ac_val} / 1000 = {vc_bond:.2f} kN\n")
                text_out.insert(0, f"  输入剪力设计值 V = {load_val:.2f} kN\n")
                if load_val > vc_bond:
                    text_out.insert(0, "  ❌ 警告：受剪粘结承载力不足!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 受剪粘结校验通过\n\n")

                stress_actual = (1.5 * (bm_val * 1e6) * y0_val) / ic_val
                text_out.insert(0, "[4. 受弯胶层验算 (规程 7.2.5)]\n")
                text_out.insert(0, f"  计算式(7.2.5): (1.5 · M · y0) / I <= fct\n")
                text_out.insert(0, f"  计算实际边缘拉应力 = (1.5 × {bm_val}×10^6 × {y0_val}) / {ic_val:.2e} = {stress_actual:.2f} MPa\n")
                text_out.insert(0, f"  胶层抗拉强度限值 fct = {fct_val:.2f} MPa\n")
                if stress_actual > fct_val:
                    text_out.insert(0, "  ❌ 警告：胶层受弯拉应力超出限值!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 胶层受弯验算通过\n")

            # === 7.3 胶栓混合连接 (规程第 7.3 节) ===
            elif "7.3" in project:
                fcv_h = float(self.entry_h_fcv.get())
                ac_h = float(self.entry_h_ac.get())
                d_h = float(self.entry_h_d.get())
                n_h = int(self.entry_h_n.get())
                v_design = float(self.entry_load.get())

                text_out.insert(0, "[1. 胶栓混合连接节点设计 (规范第 7.3 节)]\n")
                text_out.insert(0, "  • 依据规程第 7.3.3 条：结构分析时，胶栓混合连接节点可假定为刚接节点。\n")
                text_out.insert(0, "  • 依据规程第 7.3.4 条：极限状态下胶层开裂贯通，极限承载力由胶层剪切与螺栓群共同贡献。\n\n")
                
                vc_h = 0.9 * fcv_h * ac_h / 1000.0
                text_out.insert(0, "[2. 胶层抗剪阶段贡献验算 (规程 7.2.4)]\n")
                text_out.insert(0, f"  胶层抗剪承载力 V_glue = 0.9 × fcv × Ac = 0.9 × {fcv_h} × {ac_h} / 1000 = {vc_h:.2f} kN (式 7.2.4)\n\n")

                ab_area_h = math.pi * (d_h**2) / 4.0
                f_nv_val = 140.0
                n_bt_v_h = n_h * f_nv_val * ab_area_h / 1000.0
                text_out.insert(0, "[3. 螺栓群协同承载阶段验算 (规程 7.3.4)]\n")
                text_out.insert(0, f"  螺栓抗剪承载力 V_bolt = n · f_nv · Ab = {n_h} × {f_nv_val} × {ab_area_h:.2f} / 1000 = {n_bt_v_h:.2f} kN (式 7.1.9-4)\n\n")

                total_node_cap = vc_h + n_bt_v_h
                text_out.insert(0, "[4. 胶栓混合连接节点承载力综合评定]\n")
                text_out.insert(0, f"  混合节点总抗剪承载力 Nu = V_glue + V_bolt = {vc_h:.2f} + {n_bt_v_h:.2f} = {total_node_cap:.2f} kN\n")
                text_out.insert(0, f"  输入节点设计剪力 V = {v_design:.2f} kN\n")

                if v_design > total_node_cap:
                    text_out.insert(0, "  ❌ 警告：混合连接节点承载力不足 (V > Nu)!\n")
                    is_all_passed = False
                else:
                    text_out.insert(0, "  ✔ 校验通过：V <= Nu\n")

            if self.is_known_load.get():
                if is_all_passed:
                    text_out.insert(0, "\n★★★ 最终结论：设计满足要求。 ★★★\n")
                else:
                    text_out.insert(0, "\n！！！ 最终结论：设计不满足要求！请检查上方 ❌ 警告项。 ！！！\n")

        except Exception as e:
            text_out.insert(0, f"\n❌【计算错误】 详情: {str(e)}\n请检查输入参数是否正确！\n")

        return text_out.get_result()

# ================= 网页前端界面渲染 =================
st.info("💡 操作提示：请在左侧面板设置好材料、截面及荷载参数，随后点击下方按钮一键生成验算报告。")
st.info("⚠️ 免责声明：本程序依据 T/CECS 692-2020 规程编制，计算结果仅供辅助参考，实际工程应用请以人工复核及正式施工图为准。")
st.info("Support by IntelliMat Design @Chemlead")

if st.button("▶ 开始计算并生成报告", type="primary", use_container_width=True):
    with st.spinner("正在严格按照 T/CECS 692-2020 规范执行力学验算..."):
        runner = StreamlitCalculatorRunner()
        report_text = runner.run_calculation_logic()
        
        st.subheader("📋 计算报告书")
        st.text_area("详细计算过程与校验结果", report_text, height=550)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="💾 下载计算报告 (.txt)",
                data=report_text,
                file_name="TCECS692_Calculation_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            html_data = f"<html><head><meta charset='utf-8'><title>计算报告书</title></head><body style='font-family:Consolas; font-size:14px;'><pre>{report_text}</pre></body></html>"
            st.download_button(
                label="🌐 下载网页报告 (.html)",
                data=html_data,
                file_name="TCECS692_Calculation_Report.html",
                mime="text/html",
                use_container_width=True
            )
