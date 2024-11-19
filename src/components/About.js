// About.js
import React from 'react';

const About = () => {
  return (
    <div className="pt-32 min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">About Us</h2>
          <div className="prose max-w-none">
            <p className="text-lg text-gray-600 mb-6">
              Welcome to College Guide, your trusted companion in finding the perfect engineering college in Maharashtra. 
              Our platform is dedicated to helping students make informed decisions about their educational future.
            </p>
            <div className="grid md:grid-cols-2 gap-8 mt-8">
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-blue-900 mb-4">Our Mission</h3>
                <p className="text-gray-600">
                  To provide comprehensive, unbiased information about engineering colleges, enabling students 
                  to make well-informed decisions about their higher education.
                </p>
              </div>
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-blue-900 mb-4">Our Vision</h3>
                <p className="text-gray-600">
                  To become the most trusted platform for educational guidance, helping every student 
                  find their ideal path in engineering education.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;