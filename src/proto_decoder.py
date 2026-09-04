"""
轻量级纯 Python 原生 Protobuf 解码器，用于从 Antigravity 的 gen_metadata 中高效提取 Token 使用量。
无任何外部第三方依赖。
"""

def parse_varints(data: bytes):
    """解析 protobuf varint 及 length-delimited 字段"""
    res = []
    i = 0
    length_data = len(data)
    while i < length_data:
        tag = data[i]
        i += 1
        wire = tag & 7
        field = tag >> 3
        if field == 0:
            break
        if wire == 0:  # varint
            val = 0
            shift = 0
            while i < length_data:
                b = data[i]
                i += 1
                val |= (b & 0x7f) << shift
                if not (b & 0x80):
                    break
                shift += 7
            res.append((field, val))
        elif wire == 2:  # length delimited
            length = 0
            shift = 0
            while i < length_data:
                b = data[i]
                i += 1
                length |= (b & 0x7f) << shift
                if not (b & 0x80):
                    break
                shift += 7
            if i + length > length_data:
                break
            res.append((field, data[i:i + length]))
            i += length
        elif wire == 1:  # 64-bit
            i += 8
        elif wire == 5:  # 32-bit
            i += 4
        else:
            break
    return res

def extract_usage_from_blob(blob: bytes) -> dict:
    """
    从单个 gen_metadata 数据块中提取 Token 与时间性能指标:
    - prompt: 未缓存输入 Token (field 2)
    - candidates: 模型输出 Token (field 3)
    - cached: 缓存命中 Token (field 5)
    - thinking: 深度思考/推理 Token (field 9)
    - ttft: 首 token 耗时（秒，field 11）
    - streaming_duration: 输出流式传输耗时（秒，field 12）
    """
    if not blob:
        return {}

    usage = {}
    try:
        outer_fields = parse_varints(blob)
        for f_num, val in outer_fields:
            if f_num == 1 and isinstance(val, bytes):
                inner_fields = parse_varints(val)
                u_dict = {}
                ttft = 0.0
                stream_dur = 0.0
                for sf_num, sval in inner_fields:
                    if sf_num == 4 and isinstance(sval, bytes):
                        u_fields = parse_varints(sval)
                        u_dict = dict([(k, v) for k, v in u_fields if not isinstance(v, bytes)])
                    elif sf_num == 11 and isinstance(sval, bytes):
                        d = dict(parse_varints(sval))
                        ttft = d.get(1, 0) + d.get(2, 0) / 1e9
                    elif sf_num == 12 and isinstance(sval, bytes):
                        d = dict(parse_varints(sval))
                        stream_dur = d.get(1, 0) + d.get(2, 0) / 1e9

                if 2 in u_dict or 3 in u_dict:
                    usage = {
                        'prompt': u_dict.get(2, 0),
                        'candidates': u_dict.get(3, 0),
                        'cached': u_dict.get(5, 0),
                        'thinking': u_dict.get(9, 0),
                        'ttft': ttft,
                        'streaming_duration': stream_dur
                    }
    except Exception:
        pass

    return usage

