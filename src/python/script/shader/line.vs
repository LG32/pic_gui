#version 330 core
layout (location = 0) in vec2 aPos;

// out vec2 TexCoord;

// uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// flat out vec3 startPos;
// out vec3 vertPos;

void main()
{
    vec4 pos = projection * view * vec4(aPos, 0.0f, 1.0f);
	gl_Position = pos;
	// TexCoord = vec2(aTexCoord.x, aTexCoord.y);

    // startPos = pos.xyz / pos.w;
    // vertPos = startPos;
}