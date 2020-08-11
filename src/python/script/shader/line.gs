#version 330 core
layout (lines) in;
layout (line_strip, max_vertices = 50) out;

// uniform float dir_factor;
uniform vec2  u_resolution;
// flat out vec3 startPos;
// out vec3 vertPos;
out float dist;

vec3 bezier(vec3 p0, vec3 p1, vec3 p2, vec3 p3, float t) {
    return p0 * pow(1 - t, 3) 
        + 3 * p1 * t * pow(1 - t, 2)
        + 3 * p2 * pow(t, 2) * (1 - t)
        + p3 * pow(t, 3);
}

void main() {    
    vec4 lineStart = gl_in[0].gl_Position;
    vec4 lineEnd = gl_in[1].gl_Position;

    vec3 p0 = lineStart.xyz / lineStart.w;
    vec3 p3 = lineEnd.xyz / lineEnd.w;

    vec3 c = normalize(cross(p3-p0, vec3(0, 0, 1)));

    float lineLen = length((p3.xy - p0.xy) * u_resolution / 2.0);
    float outLen = length(c.xy * u_resolution / 2.0);
    float scale = lineLen * 0.2 / outLen;

    vec3 p1 = c * scale + p0 + (p3 - p0) * 0.2f;
    vec3 p2 = mix(p1, p3, 0.3);

    dist = 0.0f;
    vec3 prevVert = lineStart.xyz / lineStart.w;

    for(int i = 0; i < 50; i++) {
        float f = i / 49.0f;

        vec3 pos = bezier(p0, p1, p2, p3, f);
        gl_Position = vec4(pos, 1.0f);

        vec3 curVert = pos;
        vec2 dir = (curVert.xy - prevVert.xy) * u_resolution / 2.0;
        dist += length(dir);

        EmitVertex();

        prevVert = curVert;
    }

    EndPrimitive();
}  