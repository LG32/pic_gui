#version 330 core
out vec4 FragColor;

// in vec2 TexCoord;
// flat in vec3 startPos;
// in vec3 vertPos;
in float dist;

uniform vec2  u_resolution;
uniform float u_dashSize;
uniform float u_gapSize;

// texture samplers
// uniform sampler2D texture;
// uniform vec4 color;

void main()
{
	// linearly interpolate between both textures (80% container, 20% awesomeface)
	// FragColor = texture(texture, TexCoord);
    // vec2  dir  = (vertPos.xy-startPos.xy) * u_resolution/2.0;
    // float dist = length(dir);

    if (fract(dist / (u_dashSize + u_gapSize)) > u_dashSize/(u_dashSize + u_gapSize))
        discard; 

    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    // FragColor = color;
}