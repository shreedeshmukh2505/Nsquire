// Features.js
import React from 'react';

const Features = () => {
  return (
    <div className="pt-32 min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Advanced Search</h3>
              <p className="text-gray-600">
                Find colleges based on multiple criteria including location, courses, fees, and placement records.
              </p>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-blue-900 mb-4">College Comparison</h3>
              <p className="text-gray-600">
                Compare multiple colleges side by side to make informed decisions.
              </p>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Real-time Updates</h3>
              <p className="text-gray-600">
                Get latest updates about admission dates, fees, and placement statistics.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;