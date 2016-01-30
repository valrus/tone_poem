---VERTEX SHADER---
#ifdef GL_ES
precision highp float;
#endif

#define pi 3.1415926

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute vec2     vPosition;
attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;
uniform float      opacity;

void main(void) {
    frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
    /*
    tex_coord0 = vec2(256.0 + 256.0 * cos(2.0 * pi * vertexNum / numVertices),
                      256.0 + 256.0 * sin(2.0 * pi * vertexNum / numVertices));
    tex_coord0 = vTexCoords0;
    */
    gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}

---FRAGMENT SHADER---
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;

/* uniform texture samplers */
// uniform sampler2D  texture0;
uniform vec4       edges[12];
uniform float      darknesses[12];
uniform float      fNumSides;
uniform vec2       centerCoords;
uniform vec2       resolution;

float pointToLine(vec2 p0, vec4 seg) {
    /* https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points */
    float rise = seg.q - seg.t;
    float run = seg.p - seg.s;
    return abs(rise * p0.x - run * p0.y + seg.p * seg.t - seg.q * seg.s) / sqrt(rise * rise + run * run);
}

void main(void) {
    int numSides = int(fNumSides);
    vec2 cPos = gl_FragCoord.xy;
    float centerDistance = distance(cPos, centerCoords);

    // calculate the distance from the point to the closest edge
    float edgeDistance = 1.0 / 0.0;
    // omitting an edge from this list will make it light all the way to the edge
    for (int i = 0; i < numSides; i++) {
        float dist = pointToLine(cPos, edges[i]);
        float weightedDist = dist / darknesses[i];
        if (weightedDist < edgeDistance) {
            edgeDistance = weightedDist;
        }
    }

    float alpha = centerDistance / (centerDistance + edgeDistance);
    gl_FragColor = vec4(frag_color.r,
                        frag_color.g,
                        frag_color.b,
                        min(frag_color.a + alpha * alpha, 1.0));
}
